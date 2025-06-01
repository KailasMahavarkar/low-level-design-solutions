''' RFA Controller '''
from models.rfa import RFAStatus
from models.users import User
import requests
from logs import logger
from operations import start_operation
from persistance.rfa import load_persisted_rfa, persist_rfa, delete_persisted_rfa, RFA
from .events import EventsController
from typing import Union
import datetime
from ws import ws

class RFAController():
    @staticmethod
    async def resolve_rfa(rfa_id: str, status: RFAStatus, approver: Union[User, str], channel: str) -> RFA:
        ''' Approve the RFA '''
        rfa = load_persisted_rfa(rfa_id)
        if not rfa:
            raise Exception("RFA not found")
        if rfa.status is not RFAStatus.pending:
            raise Exception(f"RFA already resolved with status {rfa.status}")
        if isinstance(approver, User):
            rfa.approver = approver.email
        elif isinstance(approver, str):
            rfa.approver = approver
        rfa.status = status
        rfa.approval_channel = channel
        rfa.approval_time = datetime.datetime.now()
        await EventsController.create_event(approver, "rfa_resolved", {'rfa_id': rfa_id, 'status': status, 'channel': channel})
        persist_rfa(rfa)
        #RFAController.send_slack_notification(rfa)
        if rfa.status is RFAStatus.approved:
            if rfa.notes:
                rfa.parameters['notes'] = rfa.notes
            try:
                await start_operation(rfa.operation, rfa.parameters, rfa.id)
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                rfa = await RFAController.unresolve_rfa(rfa)
                raise e
        return rfa
    
    @staticmethod
    async def unresolve_rfa(rfa: RFA) -> RFA:
        ''' Unapprove the RFA '''
        rfa.approver = None
        rfa.status = RFAStatus.pending
        rfa.approval_channel = None
        persist_rfa(rfa)
        try:
            RFAController.send_slack_notification(rfa)
            await RFAController.ws_notify()
        except Exception as e:
            logger.error(f"Could not notify RFA unresolution because of {str(e)}")
        return rfa

    @staticmethod
    def get_rfa(rfa_id: str, user: User) -> RFA:
        ''' Get the RFA by id '''
        rfa = load_persisted_rfa(rfa_id)
        if rfa.requester != user.email and user.role is not UserRole.admin:
            raise Exception("Not enough permissions")
        return rfa
    
    @staticmethod
    def delete_rfa(rfa_id: str) -> None:
        ''' Delete the RFA by id '''
        delete_persisted_rfa(rfa_id)
            
    @staticmethod
    def send_slack_notification(rfa: RFA) -> None:
        ''' Send a slack notification '''
        raise NotImplementedError("Not implemented")

    @staticmethod
    async def ws_notify(rfa: RFA) -> None:
        ''' Notify the WS '''
        await ws.emit("rfas", rfa.model_dump())