#!/usr/bin/python3

"""
  Msg_Clean_F91
  
  plugin that receives a message from shovel clean_f90 ... for each product... python side
  - it checks if the propagation was ok.
  - it removes the product instances at the watch level
  - it posts the product again (shovel clean_f92 )

  when a product is not fully propagated, it is put in the retry list

  The post_log count should be the same as the original flow test count

"""
import os,stat,time

class Msg_Clean_F91(object): 

    def __init__(self,parent):
        pass

    def on_message(self,parent):
        import shutil

        logger = parent.logger
        msg    = parent.msg
        root   = parent.currentDir
        relp   = msg.relpath

        if 'clean_f90' in msg.headers :
           ext = msg.headers['clean_f90']
           del   msg.headers['clean_f90']
           msg.headers['clean_f91'] = ext

        else:
           logger.info("msg_log received: %s %s%s topic=%s lag=%g %s" % \
           tuple( msg.notice.split()[0:3] + [ msg.topic, msg.get_elapse(), msg.hdrstr ] ) )
           logger.error("The message received is incorrect not from shovel clean_f90")
           return False


        # build all 3 paths of a successfull propagated path

        if relp[0] != '/' : relp = '/' + relp + ext

        subs_f30_path = root + '/downloaded_by_sub_t'    + relp
        send_f50_path = root + '/sent_by_tsource2send'   + relp
        subs_f60_path = root + '/downloaded_by_sub_u'    + relp

        # propagated count 

        propagated = 0
        try   :
                if os.path.isfile(subs_f30_path) : propagated += 1
        except: pass
        try   :
                if os.path.isfile(send_f50_path) : propagated += 1
        except: pass
        try   :
                if os.path.isfile(subs_f60_path) : propagated += 1
        except: pass

        # propagation unfinished ... (or test error ?)
        # retry message screened out of on_message is taken out of retry
        # here we enforce keeping it... to verify propagation again

        if propagated != 3 :
           parent.consumer.msg_to_retry()
           return False

        # everything worked ... remove the watch file

        os.unlink(subs_f30_path)

        return True

self.plugin='Msg_Clean_F91'