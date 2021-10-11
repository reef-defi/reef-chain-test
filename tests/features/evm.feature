Feature: evm

  Scenario: Deploy erc20 contract
    Given I have a funded account
    When I deploy a contract using the Evm Create call
    Then I receive an Event with the contract address

  Scenario: Claim default account
    Given Bob has a funded account
    When bob claims the default EVM account
    Then the account is assinged to bob

# Scenario: erc20 transfer
# Given I have an erc20 contract deployed
# When I transfer 200 units to Bob
# Then Bobs erc20 balance increases by 200
