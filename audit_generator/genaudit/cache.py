"""
Acts as both a disk and memory cache for select GitHub API calls
"""

import logging
import re
import os
import json

from github import Requester, Consts

class CachingRequester(Requester.Requester):
    def __init__(self, login_or_token, cache_location):
        super().__init__(login_or_token,
                         Consts.DEFAULT_BASE_URL,
                         Consts.DEFAULT_TIMEOUT,
                         Consts.DEFAULT_USER_AGENT,
                         Consts.DEFAULT_PER_PAGE,
                         True, # verify
                         None,
                         None)

        # The regexes should have one or more match groups that will be used as
        # the key in the underlying cache. Multiple match groups will be
        # concatenated with dashes as separators.
        self.cachable_resources = {
            "pull_request": re.compile(r'^/repos/[^/]+/[^/]+/pulls/(\d+)$'),
            "commit": re.compile(r'^/repos/[^/]+/[^/]+/commits/([0-9a-f]+)$'),
            "user": re.compile(r'^/users/([^/]+)$'),
            "review": re.compile(r'^/repos/[^/]+/[^/]+/pulls/(\d+)/reviews$'),
            "paginated_review": re.compile(r'^/repositories/\d+/pulls/(\d+)/reviews(?:\?page=(\d+))?$'),
        }

        self.cache_location = cache_location
        self.cache = {}
        for keys in self.cachable_resources:
            self.cache[keys] = {}

    def _should_cache_as(self, verb, url):
        if verb != "GET":
            return None, None

        trimmed_url = url.replace('https://api.github.com', '')
        for resource, regex in self.cachable_resources.items():
            if m := regex.match(trimmed_url):
                return resource, '-'.join(m.groups())

        return None, None

    def _cache_path(self, res, ref):
        return os.path.join(self.cache_location, res, "%s.json" % str(ref))

    def _cache_dict(self, res):
        if res not in self.cache:
            raise LookupError("Cache for resource '%s' does not exist" % res)
        return self.cache[res]

    def _retrieve_from_cache(self, res, ref):
        cache_dict = self._cache_dict(res)
        if ref not in cache_dict:
            cache_dict[ref] = self._retrieve_from_disk(res, ref)
        return cache_dict[ref]

    def _retrieve_from_disk(self, res, ref):
        assert self.has_disk_cache()
        logging.debug("Pulling '%s' with ref '%s' from disk cache" % (res, ref))
        with open(self._cache_path(res, ref), 'r') as f:
            data = json.load(f)
            return data['headers'], data['body']

    def _store_in_cache(self, res, ref, headers, body):
        cache_dict = self._cache_dict(res)
        cache_dict[ref] = headers, body
        if self.has_disk_cache():
            self._store_on_disk(res, ref, headers, body)

    def _store_on_disk(self, res, ref, headers, body):
        item_path = self._cache_path(res, ref)
        cache_path = os.path.dirname(item_path)
        if not os.path.isdir(cache_path):
            os.makedirs(cache_path)
        with open(item_path, 'w+') as f:
            json.dump({"headers": headers, "body": body}, f)

    def contains(self, res, ref):
        if ref in self._cache_dict(res):
            return True
        elif self.has_disk_cache():
            return os.path.isfile(self._cache_path(res, ref))
        else:
            return False

    def has_disk_cache(self):
        return self.cache_location is not None

    # This hooks into PyGithub's Requester, intercepts all network requests
    # to GitHub's API and injects cached items as needed
    def _Requester__requestEncode(self, cnx, verb, url, parameters, headers, input, encode):
        res, ref = self._should_cache_as(verb, url)
        should_cache = res != None

        if should_cache and self.contains(res, ref):
            return 200, *self._retrieve_from_cache(res, ref)

        if should_cache:
            logging.debug("Fetching '%s' with ref '%s' from GitHub with caching" % (res, ref))
        else:
            logging.warning("Fetching '%s' without caching" % url)

        status, headers, body = super()._Requester__requestEncode(cnx, verb, url, parameters, headers, input, encode)
        if should_cache and status < 400:
            self._store_in_cache(res, ref, headers, body)

        return status, headers, body
