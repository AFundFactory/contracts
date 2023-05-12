# Contracts

This contract is a factory to create crowdfunding campaign smart contracts.

The contract is simple: it has the main contract `CrowdfundingDapp`, which is the factory, and a `Crowdfunding` contract that is generated by the factory for every campaign. The main contract has an entry point called `create_crowdfunding` that requires a title, description, goal, URL (can be empty), category and an ASCII string with a predefined size (currently 40x22). Categories are constrained to the ones available in the contract storage.

When the entry point is called, a `Crowdfunding` contract is deployed containing all the info of the campaign. Besides the info already provided to the factory contract, this `Crowdfunding` contract also stores the campaign's owner address, a `Closed` field and the contract version. This contract only has two entry points: one to send funds to the owner and another that allows the owner to close the campaign. Closing the campaign means that it can no longer receive funds. This contract doesn't have any other information, so it can only be controlled by the owner - neither the `CrowdfundingDapp` contract nor its admin can control it.

Current contract: KT1JmsJTJd9LwtCxZLmX28PYTdBAqrV5kUps


