
export enum Platform {
  XHS = '小红书',
  Xianyu = '咸鱼'
}

export interface SearchItem {
  id: string;
  merchantName: string;
  productFullName: string;
  price: string;
}

export interface SearchParams {
  platform: Platform;
  items: SearchItem[];
  searchCount: number;
  focusItemId: string; // New parameter to track which specific row is selected
}

export interface AnalysisResult {
  summary: string;
  recommendations: string[];
}
