import sys
import requests
import ovh
import ipaddress
import logging

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
                'unable to get record ID for given %s zonename '
                'for network reason' % zonename)
            logger.debug(e)
        except ovh.InvalidResponse:
            logger.error(
                'invalid respond while getting record ID '
                'for given zonename' % zonename)
            logger.debug(e)
        except Exception as e:
            logger.error(
                'unknown error while getting record ID '
                'for zonename %s' % zonename)
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
            logger.error('unable to get record %s for network reason' % recid)
            logger.debug(e)
        except ovh.InvalidResponse:
            logger.error('invalid respond while getting record %s' % recid)
            logger.debug(e)
        except Exception as e:
            logger.error('unknown error while getting record %s' % recid)
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
                    logger.error(e)
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

        logger.info('Update dynhost record %s:%s with IP %s' % (zonename,
                                                                recid,
                                                                ip))

        try:
            self._client.put(
                '/domain/zone/%s/dynHost/record/%s' % (zonename, recid),
                **{'ip': ip})
        except ovh.HTTPError as e:
            logger.error(
                'unable to update record %s for network reason' % recid)
            logger.debug(e)
        except ovh.InvalidResponse:
            logger.error('invalid respond while updating record %s' % recid)
            logger.debug(e)
        except Exception as e:
            logger.error('unknown error while updating record %s' % recid)
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
        logger.error(e)
    else:
        if req.status_code == 200:
            try:
                ipaddress.IPv4Address(req.text)
            except ipaddress.AddressValueError:
                logger.error('Current IP Address %s is invalid' % req.text)
            except:
                logger.error(e)
            else:
                ip = req.text
        else:
            logger.error('Unable to get current IP Address')
    finally:
        return ip


def main(dynhosts=None):
    '''
    main function
    '''
    # check if a consumer key was supplied
    _config = ovh.config.config
    if _config.get(_config.get('default', 'endpoint'), 'consumer_key') is None:
        return 1

    dynapi = DynhostWrapper(dynhosts=dynhosts)
    dynapi.update()

    return 0


if __name__ == "__main__":
    try:
        import config
    except:
        logger.error('Config file was not found')
        sys.exit(1)
    else:
        # setting log level according to value specified in config file
        if hasattr(config, 'LOG_LEVEL'):
            logger.setLevel(getattr(logging, config.LOG_LEVEL))

        sys.exit(main(dynhosts=config.DYNHOSTS))
