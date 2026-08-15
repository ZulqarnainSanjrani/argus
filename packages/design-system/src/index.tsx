import type {HTMLAttributes,ReactNode} from 'react'; import './tokens.css';
export const FactBadge=({type}:{type:'FACT'|'CALCULATED'|'ARGUS VIEW'})=><span className={`fact-badge ${type.toLowerCase().replace(' ','-')}`}>{type}</span>;
export const StatusBadge=({status}:{status:string})=><span className={`status-badge status-${status.toLowerCase()}`}>{status}</span>;
export const MarketChange=({value,unit=''}:{value:number;unit?:string})=><span className={`market-change ${value>0?'positive':value<0?'negative':'neutral'}`}>{value>0?'▲':value<0?'▼':'→'} {value>0?'+':''}{value.toFixed(2)}{unit}</span>;
export function Panel({title,eyebrow,actions,children,className='',...rest}:{title:string;eyebrow?:string;actions?:ReactNode;children:ReactNode}&HTMLAttributes<HTMLElement>){return <section className={`panel ${className}`} {...rest}><header className="panel-header"><div><span className="panel-eyebrow">{eyebrow}</span><h2>{title}</h2></div><div>{actions}</div></header>{children}</section>}
export const SourceDisclosure=({source,observed}:{source:string;observed:string})=><footer className="source"><span>Source: {source}</span><span>Observed: {observed}</span></footer>;
export const EmptyState=({label='No data available'}:{label?:string})=><div className="state">— {label}</div>;
export const LoadingState=()=> <div className="state" aria-busy="true">Loading…</div>;
export const ErrorState=()=> <div className="state error">Unable to load data</div>;
