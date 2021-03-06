#ifndef _CMDPROVIDER_H_
#define _CMDPROVIDER_H_


#include <QtCore>
#include <QtNetwork>

class CmdProvider : public QObject
{
    Q_OBJECT;
public:
    CmdProvider();
    virtual ~CmdProvider();
    
    bool init();

public slots:
    void onCometClientReadyRead();
    void onCometClientConnected();
    void onCometClientDisconnected();
    void onCometClientError(QAbstractSocket::SocketError socketError);
    void onCometClientHostFound();
    void onCometClientStateChanged(QAbstractSocket::SocketState socketState);

signals:
    void newCommand(QJsonObject jcmd);

private:
    bool connectToCometServer();
    void enqueuePacket(QString pkt_str);
    void parsePacket(QString str);
    void resetCometState();

private:
    QTcpSocket *m_cmd_recv_comet_client = NULL;

    QString m_pkt_header;
    QString m_pkt_buf;
    bool m_body_found = false;
    QQueue<QJsonObject> m_q_cmds;

};

#endif /* _CMDPROVIDER_H_ */
