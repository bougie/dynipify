import sys
import requests
import ovh
import ipaddress
import logging
import argparse

logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DynhostWrapper(object):
    '''
    manage dynhost record via OVH REST API
    '''

    def __init__(self, ip=None, dynhosts=None):
        '''
        constructor

        ip
            current ip address

        dynhosts
            list of all domains to update
        '''
        self._ip = ip
        self._client = None
        self._dynhosts = dynhosts

    def connect(self):
        '''
        open a connection to the OVH API
        '''
        if self._client is None:
            logger.debug('Creating new API client instance')
            self._client = ovh.Client()

    def request_consumer_key(self):
        '''
        request a consumer key (linked with an OVH nickhandle)
        '''
        if self._client is None:
            self.connect()

        logger.debug('Requesting new consumer API key')

        access_rules = [
            {'method': 'GET', 'path': '/domain/zone/*'},
            {'method': 'PUT', 'path': '/domain/zone/*'},
        ]

        return self._client.request_consumerkey(access_rules)

    def get_record_id(self, zonename, subdomain):
        '''
        return record ID for a given `zonename` and `subdomain`

        zonename
            zone name (for example: domain.tld)

        subdomain
            sub-domain name (ex: sub if fqdn is sub.domain.tld)
        '''
        if self._client is None:
            self.connect()

        logger.debug('Getting ID of record %s.%s' % (subdomain, zonename))

        recid = None
        try:
            dynhostid = self._client.get(
                '/domain/zone/%s/dynHost/record?subDomain=%s' % (
                    zonename,
                    subdomain))

            if len(dynhostid) > 1:
                logger.debug(dynhostid)
                raise ValueError('too much records found')
            elif len(dynhostid) == 0:
                raise ValueError('no records found')
        except ovh.HTTPError as e:
            logger.error(
                'Unable to get record ID for given zonename %s and subdomain %s'
                'for network reason' % (zonename, subdomain))
            logger.debug(e)
        except ovh.InvalidResponse:
            logger.error(
                'Invalid respond while getting record ID '
                'for given zonename %s and subdomain %s' % (zonename,
                                                            subdomain))
            logger.debug(e)
        except Exception as e:
            logger.error(
                'Unknown error while getting record ID '
                'for given zonename %s and subdomain %s' % (zonename,
                                                            subdomain))
            logger.debug(e)
        else:
            recid = dynhostid[0]
        finally:
            return recid

    def get_record(self, zonename, recid):
        '''
        return record values for a given record `recid` in a given `zonename`
        '''
        if self._client is None:
            self.connect()

        logger.debug('Getting record %s' % recid)

        rec = None
        try:
            rec = self._client.get('/domain/zone/%s/dynHost/record/%s' % (
                zonename,
                recid))
        except ovh.HTTPError as e:
            logger.error(
                'Unable to get record %s for network reason '
                'on zonename %s' % (recid, zonename))
            logger.debug(e)
        except ovh.InvalidResponse:
            logger.error(
                'Invalid respond while getting record ID %s '
                'on zonename %s' % (recid, zonename))
            logger.debug(e)
        except Exception as e:
            logger.error(
                'Unknown error while getting record ID %s '
                'on zonename %s' % (recid, zonename))
            logger.debug(e)
        finally:
            return rec

    def update(self):
        '''
        update all records
        '''
        if self._client is None:
            self.connect()

        logger.info('Update dynhosts records')

        if self._dynhosts is not None:
            if self._ip is None:
                self._ip = get_current_ip()
            logger.debug('Current IP Address is %s' % self._ip)

            for host in self._dynhosts:
                try:
                    recid = self.get_record_id(
                        zonename=host.get('domain'),
                        subdomain=host.get('subdomain', None))
                    if recid is not None:
                        rec = self.get_record(
                            zonename=host.get('domain'),
                            recid=recid)
                except Exception as e:
                    logger.error('Unable to retrieve informations for update')
                    logger.debug(e)
                else:
                    if 'ip' in rec and rec['ip'] != self._ip:
                        logger.debug('Record %s need an update' % str(host))

                        self.update_record_ip(
                            zonename=host.get('domain'),
                            recid=recid,
                            ip=self._ip)
        else:
            logger.warning('No dynhosts list was specified')

    def update_record_ip(self, zonename, recid, ip):
        '''
        update IP Address for a given `recid` in a given `zonename`
        '''
        if self._client is None:
            self.connect()

        logger.info(
            'Update dynhost record ID %s on zonename %s with IP %s' % (
                recid,
                zonename,
                ip))

        try:
            self._client.put(
                '/domain/zone/%s/dynHost/record/%s' % (zonename, recid),
                **{'ip': ip})
        except ovh.HTTPError as e:
            logger.error(
                'Unable to update record ID %s on zonename %s for network '
                'reason' % (recid, zonename))
            logger.debug(e)
        except ovh.InvalidResponse:
            logger.error(
                'Invalid respond while updating record ID %s on zonename %s' % (
                    recid,
                    zonename))
            logger.debug(e)
        except Exception as e:
            logger.error(
                'Unknown error while updating record ID %s on zonename %s' % (
                    recid,
                    zonename))
            logger.debug(e)


def get_current_ip():
    '''
    get current IP address of active network link
    '''
    logger.debug('Retriving current IP Address')

    ip = None
    try:
        req = requests.get('https://api.ipify.org')
    except Exception as e:
        logger.error('Unable to get current IP Address from ipify')
        logger.debug(e)
    else:
        if req.status_code == 200:
            try:
                ipaddress.IPv4Address(req.text)
            except ipaddress.AddressValueError:
                logger.error('Current IP Address %s is invalid' % req.text)
            except Exception as e:
                logger.error('Unknown IP Address returned by ipify')
                logger.debug(e)
            else:
                ip = req.text
        else:
            logger.error(
                'Bad response from server while getting current IP Address '
                'from ipify')
    finally:
        return ip


def update(dynhosts=None, args=None):
    '''
    update function
    '''
    # check if a consumer key was supplied
    _config = ovh.config.config
    if _config.get(_config.get('default', 'endpoint'), 'consumer_key') is None:
        logger.critical(
            'You must purchase a consumer_key before starting update')
        return 1

    dynapi = DynhostWrapper(dynhosts=dynhosts)
    dynapi.update()

    return 0


def request(dynhosts=None, args=None):
    '''
    request function
    '''
    dynapi = DynhostWrapper(dynhosts=dynhosts)
    dynapi.request_consumer_key()

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='update a DYNHOST field with the OVH API')
    parser.add_argument(
        '-l', '--level',
        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'])

    # command parser
    subparsers = parser.add_subparsers(title='Available commands',
                                       help='command description')
    # consumer key handler
    parser_auth = subparsers.add_parser('auth', help='request a consumer_key')
    parser_auth.set_defaults(func=request)
    # update handler
    parser_update = subparsers.add_parser('update', help='update DNS records')
    parser_update.set_defaults(func=update)

    args = parser.parse_args()

    try:
        import config
    except ImportError:
        logger.critical('Config file was not found')
        sys.exit(1)
    except Exception as e:
        logger.critical('Unknown error while launching program')
        logger.debug(e)
        sys.exit(1)
    else:
        # setting log level according to value specified in command line
        if hasattr(args, 'level') and args.level is not None:
            logger.setLevel(getattr(logging, args.level))
        # setting log level according to value specified in config file
        elif hasattr(config, 'LOG_LEVEL'):
            logger.setLevel(getattr(logging, config.LOG_LEVEL))

        if hasattr(args, 'func'):
            sys.exit(args.func(dynhosts=config.DYNHOSTS, args=args))
        else:
            # no command name supplied : display help message
            parser.print_help()
