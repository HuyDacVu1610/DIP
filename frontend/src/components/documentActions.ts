import type {PageRead} from '../types/scanner'
export function movePageIds(pages:Pick<PageRead,'id'>[],id:string,direction:-1|1):string[]|null {
  const ids=pages.map(p=>p.id),index=ids.indexOf(id),next=index+direction
  if(index<0||next<0||next>=ids.length)return null
  ;[ids[index],ids[next]]=[ids[next],ids[index]]
  return ids
}
export function selectRemainingPage(selected:string|null,oldPages:Pick<PageRead,'id'>[],pages:Pick<PageRead,'id'>[]):string|null {
  if(pages.some(p=>p.id===selected))return selected
  const index=Math.max(0,oldPages.findIndex(p=>p.id===selected))
  return pages[Math.min(index,pages.length-1)]?.id??null
}
