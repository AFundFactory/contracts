# new smartpy version 0.17

import smartpy as sp

@sp.module
def m():
    
    class Crowdfunding(sp.Contract):
    
        def __init__(self, params):

            self.data.owner = sp.cast(params.owner, sp.address)
            self.data.title = sp.cast(params.title, sp.string)
            self.data.description = sp.cast(params.description, sp.string)
            self.data.url = sp.cast(params.url, sp.string)
            self.data.ascii = sp.cast(params.ascii, sp.string)
            self.data.category = sp.cast(params.category, sp.string)
            self.data.goal = sp.cast(params.goal, sp.mutez)
            self.data.closed = sp.cast(False, sp.bool)
            self.data.version = sp.cast(params.version, sp.string)
                
    
        @sp.entry_point
        def send_funds(self):
    
            assert sp.amount > sp.tez(0)
            assert not (sp.sender == self.data.owner)
            assert self.data.closed == False
            
            sp.send(self.data.owner, sp.amount)
    
    
        @sp.entry_point
        def close_campaign(self):
    
            assert sp.amount == sp.tez(0)
            assert sp.sender == self.data.owner
            self.data.closed = True
    
    
    class CrowdfundingFactory(sp.Contract):
        def __init__(self, admin, version):
    
            # self.contract = Crowdfunding()
            self.data.admin = sp.cast(admin, sp.address)
            self.data.categories = sp.cast(
                sp.set(
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
                ), sp.set[sp.string])
            self.data.campaign_list = sp.cast(sp.big_map(), sp.big_map[sp.address, sp.address])
            self.data.version = sp.cast(version, sp.string)
            self.data.fee = sp.cast(sp.tez(3), sp.mutez)

    
        @sp.entry_point
        def create_crowdfunding(self, params):
    
            sp.cast(params, 
                sp.record( 
                    goal = sp.mutez,
                    title = sp.string,
                    description = sp.string,
                    url = sp.string,
                    ascii = sp.string,
                    category = sp.string)
                )
    
            assert sp.amount == self.data.fee
            assert params.goal > sp.mutez(0)
            assert self.data.categories.contains(params.category)
            assert sp.sender == sp.source
            assert sp.len(params.title) <= 50
            assert sp.len(params.description) <= 1000
    
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

            contract_address = sp.create_contract(Crowdfunding, None, sp.tez(0), s)
            self.data.campaign_list[contract_address] = sp.sender
    
            sp.send(self.data.admin, sp.amount)
    
    
        @sp.entry_point
        def add_categories(self, params):

            sp.cast(params, sp.list[sp.string])
            
            assert sp.amount == sp.tez(0)
            assert sp.sender == self.data.admin
    
            for cat in params:
                self.data.categories.add(cat)
    
        
        @sp.entry_point
        def remove_categories(self, params):

            sp.cast(params, sp.list[sp.string])
            
            assert sp.amount == sp.tez(0)
            assert sp.sender == self.data.admin
    
            for cat in params:
                self.data.categories.remove(cat)
    

@sp.add_test(name = "Crowdfunding testing")
def successful():

    # dummy addresses
    admin = sp.address("tz1xadmin")
    owner = sp.address("tz1xowner")
    owner2 = sp.address("tz1xowner2")
    user1 = sp.address("tz1xuser1")
    user2 = sp.address("tz1xuser2")
    user3 = sp.address("tz1xuser3")
    
    sc = sp.test_scenario(m)
    
    version = 'v2'
    contract = m.CrowdfundingFactory(admin, version)
    sc.h1("Main contract")
    sc += contract

    sc.h2('Creating crowdfunding with wrong category')
    contract.create_crowdfunding(
        goal = sp.tez(20), 
        title = 'title',
        description = 'description',
        url = 'url',
        ascii = 'ascii',
        category = 'c').run(sender=owner2, amount = sp.tez(3), now = sp.now, valid = False)

    sc.h2('Creating crowdfunding with wrong fee')
    contract.create_crowdfunding(
        goal = sp.tez(20), 
        title = 'title',
        description = 'description',
        url = 'url',
        ascii = 'ascii',
        category = 'Science').run(sender=owner, amount = sp.tez(5), valid = False)

    sc.h2("Create crowdfunding through CrowdfundingFactory")
    contract.create_crowdfunding(
        goal = sp.tez(20), 
        title = 'title',
        description = 'description',
        url = 'url',
        ascii = 'ascii',
        category = 'Others').run(sender=owner, amount = sp.tez(3))
    
    sc.h3('Some user tries to add category')
    contract.add_categories(['c']).run(sender=user1, valid = False)

    sc.h3('Admin adds category')
    contract.add_categories(['c']).run(sender=admin)

    sc.h3('Admin adds multiple categories (repeated - works)')
    contract.add_categories(['c', 'd']).run(sender=admin)

    sc.h3('Admin removes category that doesnt exist')
    contract.remove_categories(['e']).run(sender=admin)

    sc.h3('Admin removes category that exists')
    contract.remove_categories(['d']).run(sender=admin)


    sc.h1('Crowdfunding contract')
    cf = m.Crowdfunding(
        sp.record(
            owner = owner,
            title = 'title',
            description = 'description',
            url = 'url',
            ascii = 'ascii',
            category = 'Others',
            goal = sp.tez(10),
            version = 'v2'
        )
    )

    sc += cf

    sc.h2('Users send funds')
    cf.send_funds().run(sender = user1, amount = sp.tez(4))
    cf.send_funds().run(sender = user2, amount = sp.tez(3))

    sc.h2('Owner closes campaign')
    cf.close_campaign().run(sender = owner)

    sc.h2('User tries to fund after campaign is closed')
    cf.send_funds().run(sender = user2, amount = sp.tez(3), valid = False)