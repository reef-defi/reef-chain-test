Feature: transactions

  Scenario: Charlie bonds some REEF
    Given Charlie has a funded controller and stash account
    When Charlie bonds 100000 REEF
    Then the staking pallet should reflect charlies bonding
    And charlies stash account should have 100000 REEF frozen

  Scenario: Charlie nominates to Alice
    Given charlie has 100000 REEF bonded
    When charlie nominates alice
    Then the staking pallet should be updated appropriately
