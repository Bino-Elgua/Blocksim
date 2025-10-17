import React, { useState } from "react";
import axios from "axios";

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
      const res = await axios.post("/api/chain/stake", {
        wallet_id: walletId,
        amount: stakeAmount,
      });
      if (res.data?.status === "staked") {
        onStake(walletId, stakeAmount);
        setIsOpen(false);
        alert("Staked successfully!");
      } else {
        alert("Stake failed: " + JSON.stringify(res.data));
      }
    } catch (err: any) {
      alert("Stake error: " + (err?.message ?? JSON.stringify(err)));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>Stake to Race</button>
      {isOpen && (
        <div className="modal-overlay" onClick={() => setIsOpen(false)}>
          <div className="modal-content" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
            <h3>Stake Wallet</h3>
            <input
              type="text"
              placeholder="Wallet ID (e.g., 0x123...)"
              value={walletId}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setWalletId(e.target.value)}
            />
            <input
              type="number"
              placeholder="Amount (tokens)"
              value={stakeAmount}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setStakeAmount(Number(e.target.value) || 10)}
            />
            <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
              <button onClick={handleStake} disabled={loading}>
                {loading ? "Staking..." : "Confirm"}
              </button>
              <button onClick={() => setIsOpen(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
