#ifndef TOXTUNBASE_H
#define TOXTUNBASE_H

#include <QtCore>

#include "enet/enet.h"

class ToxTunChannel;

class ToxTunBase : public QObject
{
    Q_OBJECT;
    
public:
    uint32_t nextConid();
    ToxTunChannel *peerLastChan(ENetPeer *enpeer);
    int peerChansCount(ENetPeer *enpeer);
    int peerRemoveChan(ENetPeer *enpeer, ToxTunChannel *chan);
    int peerAddChan(ENetPeer *enpeer, ToxTunChannel *chan);
    
public:
    uint32_t m_conid = 7;
    QHash<QString, QVector<QByteArray> > m_pkts;  // friendId => [pkt1/2/3]
    QMutex m_pkts_mutex;

protected:
    virtual void promiseChannelCleanup(ToxTunChannel *chan) = 0;
                                               
public slots:
    void onToxnetFriendLossyPacket(QString friendId, QByteArray packet);
    void onToxnetFriendLosslessPacket(QString friendId, QByteArray packet);
public slots:
    void promiseCleanupTimeout();
};


#endif /* TOXTUNBASE_H */
