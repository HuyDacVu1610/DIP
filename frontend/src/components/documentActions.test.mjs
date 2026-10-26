import assert from 'node:assert/strict'
import {test} from 'node:test'
import {movePageIds,selectRemainingPage} from './documentActions.ts'
const pages=['a','b','c'].map(id=>({id}))
test('move sends full permutation, never mutates input or moves past endpoints',()=>{
 assert.deepEqual(movePageIds(pages,'b',-1),['b','a','c'])
 assert.deepEqual(movePageIds(pages,'b',1),['a','c','b'])
 assert.equal(movePageIds(pages,'a',-1),null);assert.equal(movePageIds(pages,'c',1),null)
 assert.equal(movePageIds(pages,'unknown',1),null);assert.deepEqual(pages.map(p=>p.id),['a','b','c'])
})
test('keep selection across reorder/unselected delete; selected delete chooses next then previous',()=>{
 assert.equal(selectRemainingPage('b',pages,[pages[2],pages[1],pages[0]]),'b')
 assert.equal(selectRemainingPage('b',pages,pages.slice(1)),'b')
 assert.equal(selectRemainingPage('b',pages,[pages[0],pages[2]]),'c')
 assert.equal(selectRemainingPage('c',pages,pages.slice(0,2)),'b')
 assert.equal(selectRemainingPage('a',pages,[]),null)
})
