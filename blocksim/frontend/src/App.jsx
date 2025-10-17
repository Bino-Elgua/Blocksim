import React from 'react';
import { StakeWalletModal } from './components/StakeWalletModal';
import './App.css';

export default function App() {
  return (
    <div className="App">
      <h1>BlockSim Frontend (Phase1)</h1>
      <StakeWalletModal onStake={(id, amt) => console.log(`Staked ${id}: ${amt}`)} />
    </div>
  );
}
