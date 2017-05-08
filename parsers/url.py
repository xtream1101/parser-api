import re
import shutil
import logging
import urllib.request

logger = logging.getLogger(__name__)

tld_file = './resources/tld_list.dat'
re_parse_args = re.compile('(?:(?P<arg>\w+)=?(?P<value>[^&]*))')


def _load_tld_list():
    logger.info("load_tld_list")

    tld_list_url = 'https://publicsuffix.org/list/public_suffix_list.dat'
    with urllib.request.urlopen(tld_list_url) as response, open(tld_file, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def _get_suffix_list(source):
    suffix_list = []
    logger.info("_get_suffix_list")
    for _ in range(2):
        try:
            with open(source, 'r') as list_file:
                lines = list_file.readlines()
                for line in lines:
                    line = line.strip()
                    if line == '// ===END ICANN DOMAINS===':
                        break

                    if not line.startswith('//'):
                        suffix_list.append(line.lower())
            break
        except FileNotFoundError:
            load_tld_list()

    return suffix_list


def _create_url_regex(suffix=None):
    if suffix is None:
        # Lets try and find it
        suffix = '[-\w]+\.xn--[-\w]+|[-\w]{{3,}}|[-\w]{{1,2}}\.[-\w]{{3}}|[-\w]{{2}}'
    else:
        suffix = suffix.replace('.', '\.')

    p = re.compile(('^'
                    # Parse the protocol
                    '(?:(?P<protocol>\w+)?:?\/\/)?'

                    # Parse HTTP Auth
                    '(?:(?P<username>.*):(?P<password>.*)@)?'

                    # Parse all subdomains together
                    '(?:(?P<subdomains>(?:[-\w+\.])+?)\.)?'

                    # Parse root domain
                    '(?P<rootdomain>[-\w]+)'

                    # Parse Suffix
                    '(?:\.(?P<suffix>(?:{suffix})))'

                    # Parse port
                    '(?:\:(?P<port>\d+))?'

                    # Parse endpoint
                    '(?P<endpoint>\/[^\?\s]*?)?'

                    # Parse arguments
                    '(?:\?(?P<args>[^#\s]*))?'

                    # Parse hash
                    '(?P<hash>\#[^\s]*)?'

                    # End string
                    '$').format(suffix=suffix), re.VERBOSE)
    return p


def _find_url_suffix(test_url):
    """
    Find the suffix of the url
    Use the list from https://publicsuffix.org/list/
    """
    global _global_suffix_list
    matched_suffix = None
    matched_suffix_len = 0
    matched_suffix_end_pos = 0
    # Strip the test domain down so we do not try to find the suffix in the args or path
    test_url_suffix_check = test_url.split('://')[-1].split('/')[0].lower()
    # Loop through all posiable suffix's to see if any are in the url
    for suffix in _global_suffix_list:
        suffix_idx = test_url_suffix_check.rfind(suffix)  # Returns -1 if no match is found
        if suffix_idx > -1:
            # Find the end position of the suffix
            suffix_len = len(suffix)
            end_pos = suffix_idx + suffix_len

            # The one that is furthest to the right (and the longest if 2 have the same end pos) is the correct one
            if end_pos > matched_suffix_end_pos or\
               (end_pos == matched_suffix_end_pos and suffix_len > matched_suffix_len):
                matched_suffix = suffix
                matched_suffix_len = suffix_len
                matched_suffix_end_pos = end_pos

    logger.info("Found suffix `{0}` for domain `{1}`".format(matched_suffix, test_url_suffix_check))
    return matched_suffix


def _parse_args(raw_args):
    results = re.findall(re_parse_args, raw_args)

    arg_dict = {}
    for result in results:
        tmp_arg, tmp_val = result
        if tmp_arg not in arg_dict:
            # Create new key and set the value
            if tmp_val == '':
                tmp_val = True

            arg_dict[tmp_arg] = tmp_val

        elif isinstance(arg_dict[tmp_arg], str):
            # Second value for an arg. Convert value to be a list of values
            arg_dict[tmp_arg] = [arg_dict[tmp_arg], tmp_val]

        elif isinstance(arg_dict[tmp_arg], list):
            # Already has multiple values. Append new value
            arg_dict[tmp_arg].append(tmp_val)

    return arg_dict


def check_url(test_url):
    rdata = {'input': test_url,
             'valid_tld': False,
             'parts': {'protocol': None,
                       'username': None,
                       'password': None,
                       'hash': None,
                       'subdomains': None,
                       'rootdomain': None,
                       'suffix': None,
                       'port': None,
                       'endpoint': None,
                       'args': None,
                       },
             }

    # Get suffix
    suffix = _find_url_suffix(test_url)
    if suffix is None:
        return rdata

    # Something matched lets check the rest of the url
    # Create regex pattern
    p = _create_url_regex(suffix)
    try:
        raw_parts = re.search(p, test_url)

        if raw_parts is None:
            # Something went wrong
            return rdata

        rdata['valid_tld'] = True

        raw_parts = raw_parts.groupdict()
        rdata['parts']['protocol'] = raw_parts.get('protocol')
        rdata['parts']['username'] = raw_parts.get('username')
        rdata['parts']['password'] = raw_parts.get('password')
        rdata['parts']['hash'] = raw_parts.get('hash')
        rdata['parts']['rootdomain'] = raw_parts.get('rootdomain')
        rdata['parts']['suffix'] = raw_parts.get('suffix')
        rdata['parts']['port'] = raw_parts.get('port')
        rdata['parts']['endpoint'] = raw_parts.get('endpoint')

        if raw_parts['subdomains'] is not None:
            # Convert subdomians to a list
            if '.' in raw_parts['subdomains']:
                rdata['parts']['subdomains'] = raw_parts['subdomains'].split('.')
            else:
                rdata['parts']['subdomains'] = raw_parts['subdomains']

        if raw_parts.get('args') is not None:
            rdata['parts']['args'] = _parse_args(raw_parts['args'])

    except Exception:
        logger.exception("Something went wrong parsing the url")

    return rdata

# Update list on start
_load_tld_list()
# Get list of data
_global_suffix_list = _get_suffix_list(tld_file)
