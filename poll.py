# from https://gist.github.com/gustaebel/b58e887ba93a4d0eba102dae871e11af

"""Very basic select.poll() implementation for Windows using select.select().
Developed for and tested with https://github.com/pyradius/pyrad only.

Usage:

    import poll
    poll.install()

    import select
    poller = select.poll()
    poller.register(...)
"""

import select


class Poller:
    """Basic select.poll() implementation for Windows.
    """

    def __init__(self):
        self.r = []
        self.w = []
        self.e = []

    def register(self, sock, eventmask=None):
        if eventmask is None:
            eventmask = select.POLLIN | select.POLLOUT | select.POLLPRI

        if eventmask & select.POLLIN or eventmask & select.POLLERR:
            self.r.append(sock)
        if eventmask & select.POLLOUT:
            self.w.append(sock)
        if eventmask & select.POLLPRI:
            self.e.append(sock)

    def unregister(self, sock):
        for l in (self.r, self.w, self.e):
            try:
                l.remove(sock)
            except IndexError:
                pass

    def _poll(self, timeout):
        if timeout is None:
            r, w, e = select.select(self.r, self.w, self.e)
        else:
            r, w, e = select.select(self.r, self.w, self.e, int(timeout / 1000))

        sockets = set(r) | set(w) | set(e)
        for sock in sockets:
            event = 0
            if sock in r:
                event |= select.POLLIN
            if sock in w:
                event |= select.POLLOUT
            if sock in e:
                event |= select.POLLPRI
            yield sock, event

    def poll(self, timeout=None):
        return list(self._poll(timeout))


def install():
    select.poll = Poller
    select.POLLIN = 1
    select.POLLOUT = 2
    select.POLLPRI = 4
    select.POLLERR = 8