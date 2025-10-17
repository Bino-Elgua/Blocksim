import React, { useState } from "react";
import axios from "axios";
import styles from "./StakeWalletModal.module.css";

interface Props {
  onStake: (walletId: string, amount: number) => void;
}

export const StakeWalletModal: React.FC<Props> = ({ onStake }) => {
  const [walletId, setWalletId] = useState<string>("");
  const [stakeAmount, setStakeAmount] = useState<number>(10);
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);

  const handleStake = async () => {
    if (!walletId.trim()) {
      alert("Enter wallet ID");
      return;
    }
    setLoading(true);
    try {
      const res = await axios.post("/api/chain/stake", { wallet_id: walletId, amount: stakeAmount });
      if (res.data?.status === "staked") {
        onStake(walletId, stakeAmount);
        setIsOpen(false);
        alert("Staked successfully!");
      } else {
        alert("Unexpected response: " + JSON.stringify(res.data));
      }
    } catch (err: any) {
      alert("Stake failed: " + (err?.message ?? JSON.stringify(err)));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>Stake to Race</button>
      {isOpen && (
        <div className={styles.modalOverlay} onClick={() => setIsOpen(false)}>
          <div className={styles.modalContent} onClick={(e: React.MouseEvent) => e.stopPropagation()}>
            <h3>Stake Wallet</h3>
            <input value={walletId} onChange={(e) => setWalletId(e.target.value)} placeholder="Wallet ID (e.g., 0x123...)" />
            <input value={stakeAmount} onChange={(e) => setStakeAmount(Number(e.target.value) || 10)} type="number" placeholder="Amount (tokens)" />
            <div className={styles.actions}>
              <button onClick={handleStake} disabled={loading}>{loading ? "Staking..." : "Confirm"}</button>
              <button onClick={() => setIsOpen(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
