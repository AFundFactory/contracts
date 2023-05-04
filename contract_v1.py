import time
import smartpy as sp

class Crowdfunding(sp.Contract):

    def __init__(self):

        self.init_type(
            sp.TRecord(
                owner = sp.TAddress,
                title = sp.TString,
                description = sp.TString,
                url = sp.TString,
                ascii = sp.TString,
                category = sp.TString,
                goal = sp.TMutez,
                closed = sp.TBool,
                version = sp.TString
            )
        )


    @sp.entry_point
    def send_funds(self):

        sp.verify(sp.amount > sp.tez(0))
        sp.verify(~(sp.sender == self.data.owner))
        sp.verify(self.data.closed == False)
        
        sp.send(self.data.owner, sp.amount)


    @sp.entry_point
    def close_campaign(self):

        sp.verify(sp.amount == sp.tez(0))
        sp.verify(sp.sender == self.data.owner)
        self.data.closed = True


class CrowdfundingDapp(sp.Contract):
    def __init__(self, admin, version):

        self.contract = Crowdfunding()
        self.init(
            admin = admin,
            categories = sp.set([
                'Art',
                'Blockchain',
                'Business',
                'Causes',
                'Education',
                'Events',
                'Humanities',
                'Personal',
                'Science',
                'Tools',
                'Others'
            ], sp.TString),
            campaign_list = sp.big_map(tkey = sp.TAddress, tvalue = sp.TAddress),
            version = version,
            fee = sp.tez(3)
        )


    @sp.entry_point
    def create_crowdfunding(self, params):

        sp.set_type(params, 
            sp.TRecord( 
                goal = sp.TMutez,
                title = sp.TString,
                description = sp.TString,
                url = sp.TString,
                ascii = sp.TString,
                category = sp.TString)
            )

        sp.verify(sp.amount == self.data.fee)
        sp.verify(params.goal > sp.mutez(0))
        sp.verify(self.data.categories.contains(params.category))
        sp.verify(sp.sender == sp.source)
        sp.verify(sp.len(params.title) <= 50)
        sp.verify(sp.len(params.description) <= 1000)

        s = sp.record(
            owner = sp.sender,
            title = params.title,
            description = params.description,
            url = params.url,
            ascii = params.ascii,
            category = params.category,
            goal = params.goal,
            closed = False,
            version = self.data.version
        )

        x = sp.create_contract(contract = self.contract, storage = s)
        self.data.campaign_list[x] = sp.sender

        sp.send(self.data.admin, sp.amount)


    @sp.entry_point
    def add_categories(self, params):

        sp.verify(sp.amount == sp.tez(0))
        sp.set_type(params, sp.TList(sp.TString))
        sp.verify(sp.sender == self.data.admin)

        sp.for cat in params:
            self.data.categories.add(cat)

    
    @sp.entry_point
    def remove_categories(self, params):

        sp.verify(sp.amount == sp.tez(0))
        sp.set_type(params, sp.TList(sp.TString))
        sp.verify(sp.sender == self.data.admin)

        sp.for cat in params:
            self.data.categories.remove(cat)
