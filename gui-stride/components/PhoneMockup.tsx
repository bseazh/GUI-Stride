
import React from 'react';

export const PhoneMockup: React.FC = () => {
  return (
    <div className="relative mx-auto w-[300px] h-[650px] bg-white rounded-[44px] border-2 border-dashed border-slate-300 flex flex-col items-center justify-center overflow-hidden shadow-sm">
      
      {/* Modern Android Punch-Hole Camera - Centered & Subtle */}
      <div className="absolute top-[18px] left-1/2 -translate-x-1/2 w-2.5 h-2.5 rounded-full bg-slate-100 border border-slate-200"></div>

      {/* Inner Screen Area Frame (Placement Guide) */}
      <div className="absolute top-[48px] bottom-[48px] left-[14px] right-[14px] border border-pink-200 bg-pink-50/10 rounded-[32px] flex flex-col items-center justify-center">
        {/* The 'Share' box has been removed as requested */}
        <div className="opacity-10 flex flex-col items-center">
          <div className="w-8 h-8 border border-slate-300 rounded-full mb-2"></div>
          <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Guide Area</span>
        </div>
      </div>

      {/* Modern Android Gesture Bar (Home Indicator) */}
      <div className="absolute bottom-[16px] left-1/2 -translate-x-1/2 w-28 h-1 bg-slate-100 rounded-full"></div>

      {/* Blueprint Annotations */}
      <div className="absolute -left-10 top-1/2 -translate-y-1/2 -rotate-90 opacity-20 pointer-events-none">
        <div className="flex items-center gap-2">
          <div className="w-16 h-[1px] bg-slate-400"></div>
          <span className="text-[8px] font-bold text-slate-500 uppercase tracking-[0.3em]">H-Alignment</span>
        </div>
      </div>
      
    </div>
  );
};
