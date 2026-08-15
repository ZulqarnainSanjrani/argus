export type Rate = {instrument:string;tenor:string;yield_percent:number;move_bp:number;previous_yield_percent:number};
export type MarketItem = {symbol:string;label:string;value:number;display:string;move:number;move_unit:'percent'|'bp'|'flat'};
export type EventItem = {time:string;region:string;event:string;importance:'HIGH'|'MEDIUM'|'LOW'};
export type SourceHealth = {source:string;status:'READY'|'STALE'|'DISABLED'|'ERROR';detail:string};
export type DemoHome = {
  environment:'DEMO'; disclaimer:string; fixture_source:string; generated_at:string;
  stale_after_seconds:number; rates:Rate[]; global_markets:MarketItem[];
  events:EventItem[]; source_health:SourceHealth[];
};
export type SnapshotObservation={symbol:string;label:string;value:number|null;unit:string;freshness:string;
  observation_date:string|null;retrieved_at:string|null;validation_status:string;source:string;source_url:string|null;
  market_status:'OFFICIAL_EOD'|null};
export type MarketSnapshot={environment:'DATA'|'DEMO';disclaimer:string;generated_at:string;observations:SnapshotObservation[]};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export async function fetchDemoHome(signal?:AbortSignal):Promise<DemoHome>{
  const response=await fetch(`${API_BASE}/api/v1/demo/home`,{signal,headers:{Accept:'application/json'}});
  if(!response.ok) throw new Error(`API returned ${response.status}`);
  return response.json() as Promise<DemoHome>;
}
export async function fetchMarketSnapshot(signal?:AbortSignal):Promise<MarketSnapshot>{
  const response=await fetch(`${API_BASE}/api/v1/public/market-snapshot`,{signal,headers:{Accept:'application/json'}});
  if(!response.ok) throw new Error(`API returned ${response.status}`);
  return response.json() as Promise<MarketSnapshot>;
}

export function isStale(generatedAt:string,staleAfterSeconds:number,now=Date.now()):boolean{
  return now-new Date(generatedAt).getTime()>staleAfterSeconds*1000;
}
