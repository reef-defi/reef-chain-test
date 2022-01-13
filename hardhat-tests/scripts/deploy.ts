// We require the Hardhat Runtime Environment explicitly here. This is optional
// but useful for running the script in a standalone fashion through `node <script>`.
//
// When running the script with `npx hardhat run <script>` you'll find the Hardhat
// Runtime Environment's members available in the global scope.
import { reef } from "hardhat";

async function main() {
  const provider = await reef.getProvider();
  const signer = await reef.getSignerByName("acc");
  const signer2 = await reef.getSignerByName("acc2");
  const alice = await reef.getSignerByName("alice");

  
  const address1 = await signer.getAddress();
  const address2 = await signer2.getAddress();
  
  await signer.claimDefaultAccount();
  await signer2.claimDefaultAccount();

  const reefBalance1 = await signer.getBalance();
  const reefBalance2 = await signer2.getBalance();
  
  console.log("Signer balance 1: ", reefBalance1.toString());
  console.log("Signer balance 2: ", reefBalance2.toString());

  
  console.log("Signer address 1: ", address1)
  console.log("Signer address 2: ", address2)


  const Greeter = await reef.getContractFactory("Greeter", signer);
  const greeter = await Greeter.deploy("Hello, Hardhat!");

  await greeter.deployed();
  await reef.verifyContract(greeter.address, "Greeter", ["Hello, Hardhat!"])

  console.log("Greeter deployed to:", greeter.address);

  await greeter.setGreeting("Danes je lep dan");
  console.log("Greeting: ", await greeter.greet());

  const Creator = await reef.getContractFactory("Creator", signer);
  console.log("Deploying creator");
  const creator = await Creator.deploy();

  await creator.deployed();
  await reef.verifyContract(creator.address, "Creator", []);

  console.log("Triggering contract creation in creator");
  const i1 = await creator.addItem("1");
  const i2 = await creator.addItem("2");

  console.log("item address: ", i1);
  console.log("item address: ", i2);

  const items = await creator.items;
  console.log("items: ", items);

  console.log("Deploying testtoken");
  const ERC20 = await reef.getContractFactory("TestToken", signer);
  const token = await ERC20.deploy("10000000000000000000000");

  await token.deployed();
  console.log(token.address)
  console.log("Token deployed");
  await reef.verifyContract(token.address, "TestToken", ["10000000000000000000000"])

  console.log("Transfering token founds")
  await token.transfer(address2, 123455);

  console.log("Signer balance 1: ", (await token.balanceOf(address1)).toString());
  console.log("Signer balance 2: ", (await token.balanceOf(address2)).toString());
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
