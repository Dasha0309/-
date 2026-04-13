import { expect } from "chai";
import pkg from "hardhat";
const { ethers } = pkg;

describe("ProtocolIntegrity", function () {
  it("Should store and return the correct IPFS hash", async function () {
    const Protocol = await ethers.getContractFactory("ProtocolIntegrity");
    const protocol = await Protocol.deploy();

    const meetingId = 101;
    const testHash = "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco";

    await protocol.storeHash(meetingId, testHash);
    expect(await protocol.getHash(meetingId)).to.equal(testHash);
  });
});