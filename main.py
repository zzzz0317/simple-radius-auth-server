from pyrad import dictionary, packet, server
import logging
import platform
from util import *
from config import config
from users import *
from zzlogger import logger

logging.basicConfig(filename="pyrad.log", level="DEBUG",
                    format="%(asctime)s [%(levelname)-8s] %(message)s")


class RadiusAuthServer(server.Server):

    def HandleAuthPacket(self, pkt):
        logger.info("Received an authentication request ID={}", pkt.id)
        try:
            if config.get("verify_message_authenticator", False):
                if not pkt.verify_message_authenticator():
                    logger.warning("Authentication request ID={} verify failed, ignore packet.", pkt.id)
                    return
            logger.debug("ID={} {}", pkt.id, pkt_to_dict(pkt))
            auth_username = pkt["User-Name"][0]
            auth_password = pkt.PwDecrypt(pkt["User-Password"][0])
            logger.info("ID={} username={}", pkt.id, auth_username)
            auth_ok, user = find_user(auth_username, auth_password)
            if auth_ok:
                reply_attr = fill_with_default_attr(user["reply_attr"])
                reply = self.CreateReplyPacket(pkt)
                add_attr_to_reply(reply, reply_attr)
                reply.code = packet.AccessAccept
                self.SendReplyPacket(pkt.fd, reply)
                logger.info("ID={} auth_ok, description={}", pkt.id, user["description"])
                logger.info("ID={} reply_attr={}", pkt.id, reply_attr)
            elif config["default"]["accept"]:
                reply_attr = fill_with_default_attr(config["default"]["accept-attr"])
                reply = self.CreateReplyPacket(pkt)
                add_attr_to_reply(reply, reply_attr)
                reply.code = packet.AccessAccept
                self.SendReplyPacket(pkt.fd, reply)
                logger.info("ID={} auth_default_accept", pkt.id)
                logger.info("ID={} reply_attr={}", pkt.id, reply_attr)
            else:
                reply = self.CreateReplyPacket(pkt)
                reply.code = packet.AccessReject
                self.SendReplyPacket(pkt.fd, reply)
                logger.info("ID={} auth_default_reject", pkt.id)
        except UnicodeDecodeError:
            logger.error("Got an UnicodeDecodeError during HandleAuthPacket, reply reject, pkt.id={}, pkt={}", pkt.id,
                         pkt_to_dict(pkt))
            reply = self.CreateReplyPacket(pkt)
            reply.code = packet.AccessReject
            self.SendReplyPacket(pkt.fd, reply)
        except Exception as e:
            logger.error("Got an error during HandleAuthPacket, reply reject, pkt.id={}, pkt={}", pkt.id,
                         pkt_to_dict(pkt))
            logger.exception(e)
            reply = self.CreateReplyPacket(pkt)
            reply.code = packet.AccessReject
            self.SendReplyPacket(pkt.fd, reply)


def pkt_to_str(pkt):
    s = "Attributes: "
    for attr in pkt.keys():
        try:
            s = s + "\n%s: %s" % (attr, pkt[attr][0])
        except Exception as e:
            s = s + "\n%s: %s" % (attr, e)
    return s


def pkt_to_dict(pkt):
    d = {}
    for attr in pkt.keys():
        try:
            d[attr] = pkt[attr][0]
        except Exception as e:
            d[attr] = e
    return d


def add_attr_to_reply(reply, reply_attr):
    for k in reply_attr.keys():
        v = reply_attr[k]
        if isinstance(v, str) or isinstance(v, int):
            reply.AddAttribute(k, v)
        elif isinstance(v, list):
            for vv in v:
                reply.AddAttribute(k, vv)


def fill_with_default_attr(attr):
    attr_default = config.get("attr", {})
    attr_append = config.get("attr_append", {})
    for k in attr_default.keys():
        if k not in attr.keys():
            attr[k] = attr_default[k]
    for k in attr_append.keys():
        vals = attr_append[k]
        if isinstance(vals, str):
            vals = [vals]
        if k in attr.keys():
            if isinstance(attr[k], str):
                attr[k] = [attr[k]]
            attr[k].extend(vals)
            attr[k] = list(set(attr[k]))
        else:
            attr[k] = attr_append[k]
    return attr


if __name__ == '__main__':
    # create server and read dictionary.txt
    if not platform.system().lower() == 'linux':
        logger.warning("System platform is not Linux, install custom poll")
        import poll

        poll.install()
    authport = config["port"]
    logger.info("Initializing RadiusAuthServer, authport={}", authport)
    srv = RadiusAuthServer(dict=dictionary.Dictionary(get_script_path_file("dict.txt")),
                           authport=authport,
                           auth_enabled=True, acct_enabled=False, coa_enabled=False)
    # add clients (address, secret, name)
    for client in config["clients"]:
        logger.info("Add client {}, secret={}", client["client"], client["secret"])
        srv.hosts[client["client"]] = server.RemoteHost("", client["secret"].encode(), "")
    # srv.hosts["10.99.0.233"] = server.RemoteHost("", b"secret12345", "")
    for addr in config["bind"]:
        logger.info("Bind to address {}", addr)
        srv.BindToAddress(addr)
    # start server
    logger.info("Start RadiusAuthServer")
    srv.Run()
