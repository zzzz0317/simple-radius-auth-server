from pyrad import dictionary, packet, server
import logging
from loguru import logger
import traceback
import platform
from util import *
from config import config
from users import *

logging.basicConfig(filename="pyrad.log", level="DEBUG",
                    format="%(asctime)s [%(levelname)-8s] %(message)s")


class RadiusAuthServer(server.Server):

    def HandleAuthPacket(self, pkt):
        logger.info("Received an authentication request ID={}", pkt.id)
        try:
            if not pkt.verify_message_authenticator():
                logger.warning("Authentication request ID={} verify failed, ignore packet.", pkt.id)
                return
            logger.debug("ID={} {}", pkt.id, pkt_to_str(pkt))
            auth_username = pkt["User-Name"][0]
            auth_password = pkt.PwDecrypt(pkt["User-Password"][0])
            logger.info("ID={} username={} password={}", pkt.id, auth_username, auth_password)
            auth_ok, reply_attr = find_user(auth_username, auth_password)
            if auth_ok:
                reply = self.CreateReplyPacket(pkt, **reply_attr)
                reply.code = packet.AccessAccept
                self.SendReplyPacket(pkt.fd, reply)
                logger.info("ID={} auth_ok\n{}", pkt.id, reply_attr)
            elif config["default"]["accept"]:
                reply = self.CreateReplyPacket(pkt, **config["default"]["accept-attr"])
                reply.code = packet.AccessAccept
                self.SendReplyPacket(pkt.fd, reply)
                logger.info("ID={} auth_default_accept\n{}", pkt.id, config["default"]["accept-attr"])
            else:
                reply = self.CreateReplyPacket(pkt)
                reply.code = packet.AccessReject
                self.SendReplyPacket(pkt.fd, reply)
                logger.info("ID={} auth_default_reject", pkt.id)
        except Exception as e:
            logger.error("Got an error during HandleAuthPacket, pkt.id={}, reply reject.\n{}\n{}", pkt.id, pkt_to_str(pkt), traceback.format_exc())
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
