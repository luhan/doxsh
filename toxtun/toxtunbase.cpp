
#include "toxtunutils.h"

#include "toxtunbase.h"

uint32_t ToxTunBase::nextConid()
{
    return this->m_conid ++;
}

/*
  QVector<ToxTunChannel*>* enpeer->toxchans
 */
ToxTunChannel *ToxTunBase::peerLastChan(ENetPeer *enpeer)
{
    ToxTunChannel *chan0 = (ToxTunChannel*)enpeer->toxchans;
    return chan0;
    return 0;
    QVector<ToxTunChannel*>* chans = (QVector<ToxTunChannel*>*)enpeer->toxchans;
    if (chans == NULL) return NULL;

    int idx = chans->count();
    if (idx == 0) return NULL;
    ToxTunChannel *chan = chans->at(idx-1);
    return chan;
    return 0;
}

int ToxTunBase::peerChansCount(ENetPeer *enpeer)
{
    ToxTunChannel *chan = (ToxTunChannel*)enpeer->toxchans;
    if (chan != NULL) return 1;
    return 0;
    
    QVector<ToxTunChannel*>* chans = (QVector<ToxTunChannel*>*)enpeer->toxchans;
    return chans->count();
}

int ToxTunBase::peerRemoveChan(ENetPeer *enpeer, ToxTunChannel *chan)
{
    ToxTunChannel *tchan0 = (ToxTunChannel*)enpeer->toxchans;
    assert(tchan0 == chan);
    enpeer->toxchans = NULL;
    return 0;
    //
    QVector<ToxTunChannel*>* chans = (QVector<ToxTunChannel*>*)enpeer->toxchans;
    int idx = -1;
    ToxTunChannel *tchan = NULL;
    
    for (int i = 0; i < chans->count(); i++) {
        tchan = chans->at(i);
        if (tchan == chan) {
            idx = i;
            break;
        }
    }

    if (idx ==  -1) {
        qDebug()<<"chan not found:"<<chan<<chan->m_conid;
        return idx;
    }

    chans->remove(idx);
    
    return idx;
}

int ToxTunBase::peerAddChan(ENetPeer *enpeer, ToxTunChannel *chan)
{
    ToxTunChannel* tchan = (ToxTunChannel*)enpeer->toxchans;
    assert(tchan == NULL);
    enpeer->toxchans = chan;
    return 1;
    //
    QVector<ToxTunChannel*>* chans = (QVector<ToxTunChannel*>*)enpeer->toxchans;
    chans->append(chan);
    return chans->count();
}

// 返回压缩后的大小
static size_t enet_simple_compress(void * context, const ENetBuffer * inBuffers, size_t inBufferCount,
                                   size_t inLimit, enet_uint8 * outData, size_t outLimit)
{
    // return 0;
    if (inLimit < 200) return 0;
    
    qDebug()<<inBufferCount<<inLimit<<outLimit;
    size_t cpsz = 0;
    QByteArray inbuf;
    
    size_t inlen = 0;
    for (int i = 0; i < inBufferCount; i ++) {
        const ENetBuffer *buffer = &inBuffers[i];
        if (inlen + buffer->dataLength > inLimit) {
            break;
        }
        inlen += buffer->dataLength;
        inbuf.append((const char*)buffer->data, buffer->dataLength);
    }

    QByteArray outbuf = qCompress(inbuf, 7);
    memcpy(outData, outbuf.data(), outbuf.length());

    if (outbuf.length() > outLimit) {
        qDebug()<<"invlid compress:"<<outbuf.length()<<outLimit<<inlen;
        return 0;
    }
    return outbuf.length();
    return 0;
}

// 返回解压后的大小
static size_t enet_simple_decompress(void * context, const enet_uint8 * inData, size_t inLimit,
                                     enet_uint8 * outData, size_t outLimit)
{
    qDebug()<<inLimit<<outLimit;

    QByteArray inbuf((const char*)inData, inLimit);
    QByteArray outbuf = qUncompress(inbuf);

    memcpy(outData, outbuf.data(), outbuf.length());
    return outbuf.length();
    return 0;
}

static void enet_simple_destroy(void * context)
{
    qDebug()<<"";
}


ENetCompressor *ToxTunBase::createCompressor()
{
    if (m_enziper == NULL) {
        m_enziper = (ENetCompressor*)calloc(1, sizeof(ENetCompressor));
        m_enziper->context = (void*)0x1;

        m_enziper->compress = enet_simple_compress;
        m_enziper->decompress = enet_simple_decompress;
        m_enziper->destroy = enet_simple_destroy;
    }

    return m_enziper;
}

void ToxTunBase::onToxnetFriendLossyPacket(QString friendId, QByteArray packet)
{
    // qDebug()<<friendId<<packet.length();
    QMutexLocker mtlck(&m_pkts_mutex);
    // put buffers
    if (!m_inpkts.contains(friendId)) {
        m_inpkts[friendId] = QQueue<QByteArray>();
    }

    m_inpkts[friendId].enqueue(packet);
    // qDebug()<<friendId<<packet.length();
}

void ToxTunBase::onToxnetFriendLosslessPacket(QString friendId, QByteArray packet)
{
    qDebug()<<friendId<<packet.length();
}

void ToxTunBase::promiseCleanupTimeout()
{
    QTimer *timer = (QTimer*)sender();
    QVariant vchan = timer->property("chan");
    ToxTunChannel *chan = (ToxTunChannel*)vchan.value<void*>();
    qDebug()<<timer<<chan<<chan->m_conid;
    this->promiseChannelCleanup(chan);
}
