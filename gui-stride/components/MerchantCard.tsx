
import React from 'react';
import { Merchant } from '../types';

interface MerchantCardProps {
  merchant: Merchant;
  isSelected: boolean;
  onSelect: (merchant: Merchant) => void;
}

export const MerchantCard: React.FC<MerchantCardProps> = ({ merchant, isSelected, onSelect }) => {
  const isPirated = merchant.status === 'pirated';

  return (
    <div 
      onClick={() => onSelect(merchant)}
      className={`flex-shrink-0 w-[140px] bg-white rounded-3xl p-3.5 transition-all cursor-pointer border-2 ${
        isSelected 
          ? 'border-indigo-600 shadow-xl scale-[1.05] z-10' 
          : 'border-slate-50 shadow-sm hover:border-slate-200'
      }`}
    >
      <div className="flex items-center justify-between mb-2.5">
        <span className={`text-[8px] font-black px-1.5 py-0.5 rounded-full uppercase tracking-tighter ${
          isPirated ? 'bg-rose-50 text-rose-500' : 'bg-emerald-50 text-emerald-500'
        }`}>
          {isPirated ? 'PIRATE' : 'OFFICIAL'}
        </span>
      </div>
      
      <div className="aspect-square rounded-2xl overflow-hidden mb-2.5 bg-slate-50">
        <img src={merchant.imageUrl} alt={merchant.name} className="w-full h-full object-cover" />
      </div>
      
      <h4 className="text-[10px] font-black text-slate-900 truncate">{merchant.name}</h4>
      <p className="text-[8px] text-slate-400 font-bold uppercase tracking-widest mt-0.5">{merchant.platform}</p>
    </div>
  );
};
