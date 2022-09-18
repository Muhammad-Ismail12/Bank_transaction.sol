//SPDX-License-Identifier: GPL-3.0

pragma solidity <0.9.0;

contract Bank{

    mapping(address => uint256) deposit;

    function _add() public payable{
        deposit[msg.sender] = msg.value;
        require(msg.value >= 5 ether , "Minimum Amount is 5 ether");
        require(msg.value <= 30 ether , "Maximum Amount is 30 ether");
    }

    function _withdraw(address _withdrawee) public payable{
        require(deposit[_withdrawee] > 0 , "Zero Balance");
        require(msg.value <= 15 ether);
    }

    function _getbalance(address _address) public view returns(uint256){
        return deposit[_address];
    }

    function getbalance() public view returns(uint256){
        return address(this).balance;
    }
}
