import sys, time

from PyQt5.QtCore import *
from pytox import *

SERVER = [
    "54.199.139.199",
    33445,
    "7F9C31FE850E97CEFD4C4591DF93FC757C7C12549DDD55F8EEAECC34FE76C029"
]

class ToxOptions():
    def __init__(self):
        self.ipv6_enabled = True
        self.udp_enabled = True
        self.proxy_type = 0 # 1=http, 2=socks
        self.proxy_host = ''
        self.proxy_port = 0
        self.start_port = 0
        self.end_port = 0
        self.tcp_port = 0
        self.savedata_type = 0 # 1=toxsave, 2=secretkey
        self.savedata_data = b''
        self.savedata_length = 0
        
class ToxDhtServer():
    def __init__(self):
        self.addr = ''
        self.port = -1
        self.pubkey = ''
        self.name = ''
        return

import os, distutils.file_util
class ToxSettings():
    def __init__(self, identifier = 'anon', persist = True):
        self.persist = persist
        self.ident = identifier
        # $HOME/.config/toxkit/{identifier}/
        self.bdir = '%s/.config/toxkit' % os.getenv('HOME')
        self.sdir = self.bdir + '/%s' % self.ident
        self.path = self.bdir + '/qtox.ini'

        self.qsets = QSettings(self.path, QSettings.IniFormat)
        self.data = self.sdir + '/tkdata'
        self.friend_list = QSettings(self.sdir + '/toxkit.friend.lst', QSettings.IniFormat)

        if persist is True:
            if not os.path.exists(self.bdir):
                os.mkdir(self.bdir)

            if not os.path.exists(self.sdir):
                os.mkdir(self.sdir)

            if not os.path.exists(self.path):
                # copy current path qtox.ini to dst
                srcfile = os.path.dirname(__file__) + '/../etc/qtox.ini'
                distutils.file_util.copy_file(srcfile, self.path)
                self.qsets = QSettings(self.path, QSettings.IniFormat)
                pass
        
        return

    def getDhtServerList(self):
        self.qsets.beginGroup('DHT Server/dhtServerList')
        stsize = int(self.qsets.value('size'))

        dhtsrvs = []
        for i in range(1, stsize+1):
            dhtsrv = ToxDhtServer()
            dhtsrv.addr = self.qsets.value('%d/address' % i)
            dhtsrv.port = int(self.qsets.value('%d/port' % i))
            dhtsrv.pubkey = self.qsets.value('%d/userId' % i)
            dhtsrv.name = self.qsets.value('%d/name' % i)
            dhtsrvs.append(dhtsrv)

        self.qsets.endGroup()
        return dhtsrvs

    def getSaveData(self):
        if self.persist is False: return b''
        
        print(self.data)
        fp = QFile(self.data)
        fp.open(QIODevice.ReadOnly)
        data = fp.readAll()
        fp.close()
        return data.data()

    def saveData(self, data):
        if self.persist is False: return 0
        if len(data) == 0: return 0
        
        fp = QFile(self.data)
        fp.open(QIODevice.ReadWrite | QIODevice.Truncate)
        n = fp.write(data)
        fp.close()
        
        return n

    def saveFriends(self, friends):
        if self.persist is False: return
        
        self.friend_list.beginGroup('FriendList')
        fn = len(friends)
        self.friend_list.setValue('size', str(fn))
        i = 0
        for fid in friends:
            self.friend_list.setValue(str(i), fid)
            i += 1
        self.friend_list.endGroup()
        return

    def loadFriends(self):
        if self.persist is False: return []
        
        self.friend_list.beginGroup('FriendList')
        fn = self.friend_list.value('size')
        if fn == None: fn = 0
        else: fn = int(fn)

        friends = []
        if fn > 0:
            for i in range(0, fn):
                fid = self.friend_list.value(str(i))
                #qDebug(fid)
                friends.append(fid)
                
        qDebug('load friend done: %d' % len(friends))
        
        ###
        hcfriends = ['398C8161D038FD328A573FFAA0F5FAAF7FFDE5E8B4350E7D15E6AFD0B993FC529FA90C343627',
                   '4610913CF8D2BC6A37C93A680E468060E10335178CA0D23A33B9EABFCDF81A46DF5DDE32954A',
                   '2645081363C7E8B5090523098A563D3BE3A6D92227B251E55FE42FBBA277500DC80EF1F7CF4A',
        ]

        for f in hcfriends:
            if f not in friends: friends.append(f)

        self.friend_list.endGroup()
        return friends


class ToxSlot(Tox):
    def __init__(self, opts):
        super(ToxSlot, self).__init__(opts)
        self.opts = opts

        #self.fwd_friend_request = None
        #self.fwd_connection_status = None
        
        return

    def on_file_recv(self, *args):
        qDebug('hehre')
        print(args)
        self.file_control(args[0], args[1], 0)
        #self.file_control(args[0], args[1], 2)
        return
    # friend_number, file_number, control
    def on_file_recv_control(self, *args):
        qDebug('herhe')
        print(args)
        return

    # (57, 65536, 19666995, b'data...')
    def on_file_recv_chunk(self, *args):
        qDebug('herhe')
        print(args[0:3])
        # print(args)
        if args[3] is None: qDebug('finished')
        else: qDebug(str(len(args[3])))
        return
    # (0, 0, 86373, 1371)
    def on_file_chunk_request(self, *args):
        qDebug(str(args))
        data = '%1371s' % 'abcdefg'
        ret = 0
        # ret = self.file_send_chunk(args[0], args[1], args[2], data)
        qDebug(str(ret))
        return
    
    def on_friend_request(self, *args):
        qDebug('herhe')
        print(args)
        return

    def on_friend_connection_status(self, *args):
        qDebug('herhe')
        print(args)
        return

### 支持qt signal slots
### 支持永久存储与不存储
class QToxKit(QThread):
    connectChanged = pyqtSignal(bool)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    friendRequest = pyqtSignal('QString', 'QString')
    friendAdded = pyqtSignal('QString')
    newMessage = pyqtSignal('QString', int, 'QString')
    friendConnected = pyqtSignal('QString')
    friendConnectionStatus = pyqtSignal('QString', bool)
    fileRecvControl = pyqtSignal('QString', int, int)
    fileRecv = pyqtSignal('QString', int, int, 'QString')
    fileRecvChunk = pyqtSignal('QString', int, int, 'QString')
    fileChunkRequest = pyqtSignal('QString', int, int, int)

    
    def __init__(self, identifier = 'anon', persist = True, parent = None):
        super(QToxKit, self).__init__(parent)
        self.sets = ToxSettings(identifier, persist)

        self.opts = ToxOptions()
        self.stopped = False
        self.is_connected = False
        self.bootstrapStartTime = None
        self.bootstrapFinishTime = None
        self.first_connected = True
        self.friends = []
        
        self.tox = Tox(self.opts)
        self.tox = None

        self.start()
        return

    def run(self):
        self.makeTox()
        
        self.bootstrapStartTime = QDateTime.currentDateTime()
        self.bootDht()

        # self.exec_()
        while self.stopped != True:
            self.itimeout()
            QThread.msleep(self.tox.iteration_interval() * 1)  # *9???

        qDebug('toxkit thread exit.')
        return

    def makeTox(self):
        self.friends = self.sets.loadFriends()
        
        self.opts.savedata_data = self.sets.getSaveData()
        qDebug(str(type(self.opts.savedata_data)))
        print(len(self.opts.savedata_data), self.opts.savedata_data[0:32])
        
        self.tox = ToxSlot(self.opts)
        myaddr = self.tox.self_get_address()
        self.tox.self_set_name('tki.' + myaddr[0:5])
        qDebug(str(self.tox.self_get_address()))
        newdata = self.tox.get_savedata()
        print(len(newdata), newdata[0:32])
        self.sets.saveData(newdata)

        # callbacks，获取回调方法的控制
        self.tox.on_friend_request = self.fwdFriendRequest
        self.tox.on_friend_connection_status = self.onFriendConnectStatus
        self.tox.on_friend_message = self.onFriendMessage
        self.tox.on_user_status = self.onFriendStatus


        # file callbacks
        self.tox.on_file_recv_control = self.onFileRecvControl
        self.tox.on_file_recv = self.onFileRecv
        self.tox.on_file_recv_chunk = self.onFileRecvChunk
        self.tox.on_file_chunk_request = self.onFileChunkRequest
        
        
        return
    
    def bootDht(self):
        dhtsrvs = self.sets.getDhtServerList()
        sz = len(dhtsrvs)
        qsrand(time.time())
        rndsrvs = {}
        while True:
            rnd = qrand() % sz
            rndsrvs[rnd] = 1
            if len(rndsrvs) >= 3: break

        localrun = False # just for convient
        # localrun = True
        if localrun is True: self.bootDHTLocal()

        #myvpsnode = ['104.238.150.157', 33445,
        #             '886568B282E280AEC7661EF3F1A2AAE809D11FB37F9E81E7D2D0758BC73B0943']
        #bsret = self.tox.bootstrap(myvpsnode[0], myvpsnode[1], myvpsnode[2])
        #rlyret = self.tox.add_tcp_relay(myvpsnode[0], myvpsnode[1], myvpsnode[2])
        #qDebug('bootstrap from: %s %d %s' % (myvpsnode[0], myvpsnode[1], myvpsnode[2]))

        myvpsnode = ['128.199.78.247', 33445,
                     '34922396155AA49CE6845A2FE34A73208F6FCD6190D981B1DBBC816326F26C6C']
        bsret = self.tox.bootstrap(myvpsnode[0], myvpsnode[1], myvpsnode[2])
        rlyret = self.tox.add_tcp_relay(myvpsnode[0], myvpsnode[1], myvpsnode[2])
        qDebug('bootstrap from: %s %d %s' % (myvpsnode[0], myvpsnode[1], myvpsnode[2]))

        # localrun = True
        qDebug('selected srvs:' + str(rndsrvs))
        for rnd in rndsrvs:
            if localrun is True: continue
            srv = dhtsrvs[rnd]
            #qDebug('bootstrap from:' + str(rndsrvs) +  str(srv))
            qDebug('bootstrap from: %s %d %s' % (srv.addr, srv.port, srv.pubkey))
            bsret = self.tox.bootstrap(srv.addr, srv.port, srv.pubkey)
            rlyret = self.tox.add_tcp_relay(srv.addr, srv.port, srv.pubkey)

        
        return

    def bootDHTLocal(self):
        mylonode = ['127.0.0.1', 33445,
                    # 'FEDCF965A96C7FBE87DFF9454980F36C43D7C1D9483E83CBD717AA02865C5B2B']
                    '320207C17B870DDDA8DDF1EEC474B2B12A26BC31F786C88EA9AB51590E916D48']   # for no network

        bsret = self.tox.bootstrap(mylonode[0], mylonode[1], mylonode[2])
        rlyret = self.tox.add_tcp_relay(mylonode[0], mylonode[1], mylonode[2])
        qDebug('bootstrap from: %s %d %s' % (mylonode[0], mylonode[1], mylonode[2]))

        return
    
    def itimeout(self):
        civ = self.tox.iteration_interval()

        self.tox.iterate()
        conned = self.tox.self_get_connection_status()
        #qDebug('hehre' + str(conned))
        
        if conned != self.is_connected:
            qDebug('connect status changed: %d -> %d' % (self.is_connected, conned))
            if conned is True: self.bootstrapFinishTime = QDateTime.currentDateTime()
            self.is_connected = conned
            self.connectChanged.emit(conned)
            self.onSelfConnectStatus(conned)
            if conned is True: self.connected.emit()
            if conned is False: self.disconnected.emit()
           
        return

    def isConnected(self):
        conned = self.tox.self_get_connection_status()
        if conned == 1: return True
        return False
    
    def onSelfConnectStatus(self, status):
        qDebug('my status: %s' % str(status))
        fnum = self.tox.self_get_friend_list_size()
        qDebug('friend count: %d' % fnum)
        # 为什么friend count是0个呢？，难道是因为没有记录吗？是因为每次加好友没有保存savedata
        # 果然是这个样子的
            
        
        friends = self.friends
        if status is True and self.first_connected:
            self.first_connected = False

            flist = self.tox.self_get_friend_list()
            qDebug(str(flist))
            for f in flist:
                s = self.tox.friend_get_status(f)
                qDebug('%d: status = %d' % (f, s))
                self.tox.friend_delete(f)

            #for friend in friends:
            #    self.tox.friend_add_norequest(friend)

            cnter = 0
            n = 0
            for friend in friends:
                if cnter < 3 or cnter >= (len(friends) - 3):
                    try:
                        self.tox.friend_add_norequest(friends[cnter])
                        pass
                    except Exception as e:
                        qDebug(str(e.args))
                    n += 1
                cnter += 1
            qDebug('add old friend: %d/%d' % (n, len(friends)))
            # self.connected.emit()
            
            newdata = self.tox.get_savedata()
            # print(len(newdata), newdata[0:32])
            self.sets.saveData(newdata)

        return

    def fwdFriendRequest(self, pubkey, data):
        qDebug(str(pubkey))
        qDebug(str(data))

        if pubkey in self.friends:
            qDebug('already in friendlist:')
            self.friendAdded.emit(pubkey)
            return
        
        self.friends.append(pubkey)
        self.sets.saveFriends(self.friends)
        
        fnum = self.tox.friend_add_norequest(pubkey)
        qDebug(str(fnum))

        self.friendAdded.emit(pubkey)
        # self.tox.send_message(fnum, 'hehe accept')

        
        newdata = self.tox.get_savedata()
        # print(len(newdata), newdata[0:32])
        self.sets.saveData(newdata)

        return
    
    def onFriendConnectStatus(self, fno, status):
        qDebug('hehre: fnum=%s, status=%s' % (str(fno), str(status)))
        friend_pubkey = self.tox.friend_get_public_key(fno)
        self.friendConnectionStatus.emit(friend_pubkey, status)
        if status is True: self.friendConnected.emit(friend_pubkey)
        if status is True:
            newdata = self.tox.get_savedata()
            # print(len(newdata), newdata[0:32])
            self.sets.saveData(newdata)

        return

    def friendAdd(self, friendId, msg):
        rc = self.tox.friend_add(friendId, msg)
        qDebug(str(rc))

        if rc < 10000:
            newdata = self.tox.get_savedata()
            # print(len(newdata), newdata[0:32])
            self.sets.saveData(newdata)
        return rc

    def friendAddNorequest(self, friendId):
        rc = self.tox.friend_add_norequest(friendId)
        qDebug(str(rc))

        if rc < 10000:
            newdata = self.tox.get_savedata()
            # print(len(newdata), newdata[0:32])
            self.sets.saveData(newdata)
        return rc
    
    def onFriendMessage(self, fno, msg_type, msg):
        # qDebug('here')
        u8msg = msg.encode('utf8') # str ==> bytes
        #print(u8msg)
        u8msg = str(u8msg, encoding='utf8')
        #print(u8msg) # ok, python utf8 string
        # qDebug(u8msg.encode('utf-8')) # should ok, python utf8 bytes
        
        fid = self.tox.friend_get_public_key(fno)
        # print('hehre: fnum=%s, fid=%s, msg=' % (str(fno), str(fid)), u8msg)
        self.newMessage.emit(fid, msg_type, msg)
        return

    def onFriendStatus(self, fno, status):
        qDebug('hehre: fnum=%s, status=%s' % (str(fno), str(status)))
        fid = self.tox.friend_get_public_key(fno)
        #if status == 0: self.friendConnected.emit(fid)
        
        return

    def friendGetConnectionStatus(self, friend_pubkey):
        friend_number = self.tox.friend_by_public_key(friend_pubkey)
        status = self.tox.friend_get_connection_status(friend_number)
        return status

    def sendMessage(self, fid, msg):
        fno = self.tox.friend_by_public_key(fid)
        mlen = 1371 - 1
        pos = 0
        while pos < len(msg):
            msgn = msg[pos:(pos + mlen)]
            pos = pos + mlen
            self.tox.friend_send_message(fno, Tox.MESSAGE_TYPE_NORMAL, msgn)
        return

    def onFileRecv(self, friend_number, file_number, kind, file_size, filename):
        qDebug('on file recv:')
        args = (friend_number, file_number, kind, file_size, filename)
        qDebug(str(args))

        friend_pubkey = self.tox.friend_get_public_key(friend_number)
        self.fileRecv.emit(friend_pubkey, file_number, file_size, filename)
        
        return

    # @param data bytes
    def onFileRecvChunk(self, friend_number, file_number, position, data):
        a = (friend_number, file_number, position, data)
        # qDebug(str(a))
        udata = data.decode('utf8')
        
        friend_pubkey = self.tox.friend_get_public_key(friend_number)
        self.fileRecvChunk.emit(friend_pubkey, file_number, position, udata)
        return

    def onFileChunkRequest(self, friend_number, file_number, position, length):
        friend_pubkey = self.tox.friend_get_public_key(friend_number)
        self.fileChunkRequest.emit(friend_pubkey, file_number, position, length)
        return

    def fileSend(self, friend_pubkey, file_size, file_name):
        friend_number = self.tox.friend_by_public_key(friend_pubkey)
        file_id = file_name
        file_number = self.tox.file_send(friend_number, 0, file_size, file_id, file_name)
        return file_number

    def fileSendChunk(self, friend_pubkey, file_number, position, data):
        friend_number = self.tox.friend_by_public_key(friend_pubkey)
        bret = self.tox.file_send_chunk(friend_number, file_number, position, data)
        return bret
    
    def fileControl(self, friend_pubkey, file_number, control):
        friend_number = self.tox.friend_by_public_key(friend_pubkey)
        bret = self.tox.file_control(friend_number, file_number, control)
        
        return bret
    
    def onFileRecvControl(self, friend_number, file_number, control):
        friend_id = self.tox.friend_get_public_key(friend_number)
        # file_id = '%128s' % ' '
        # ret = self.tox.file_get_file_id(friend_number, file_number, file_id)
        # qDebug(file_id)
        # qDebug(str(len(file_id)))

        self.fileRecvControl.emit(friend_id, file_number, control)
        
        return
