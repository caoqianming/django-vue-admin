import request from '@/utils/request'

export function getWorkflowList(query) {
  return request({
    url: '/wf/workflow/',
    method: 'get',
    params: query
  })
}
export function createWorkflow(data) {
  return request({
    url: '/wf/workflow/',
    method: 'post',
    data
  })
}
export function updateWorkflow(id, data) {
  return request({
    url: `/wf/workflow/${id}/`,
    method: 'put',
    data
  })
}
export function deleteWorkflow(id, data) {
  return request({
    url: `/wf/workflow/${id}/`,
    method: 'delete',
    data
  })
}
//流转状态列表
export function getWfStateList(id) {
  return request({
    url: `/wf/workflow/${id}/states`,
    method: 'get'
  })
}
//工单流转step
export function getWfFlowSteps(id) {
  return request({
    url: `/wf/ticket/${id}/flowsteps/`,
    method: 'get'
  })
}

//流转状态创建
export function createWfState(data) {
  return request({
    url: '/wf/state/',
    method: 'post',
    data
  })
}
//处理工单
export function ticketHandle(id,data) {
  return request({
    url: `/wf/ticket/${id}/handle/`,
    method: 'post',
    data
  })
}

//流转状态更新
export function updateWfState(id, data) {
  return request({
    url: `/wf/state/${id}/`,
    method: 'put',
    data
  })
}
//流转状态删除
export function deleteWfState(id, data) {
  return request({
    url: `/wf/state/${id}/`,
    method: 'delete',
    data
  })
}
//自定义字段列表
export function getWfCustomfieldList(id) {
  return request({
    url: `/wf/workflow/${id}/customfields`,
    method: 'get'
  })
}
//自定义字段创建
export function createWfCustomfield(data) {
  return request({
    url: '/wf/customfield/',
    method: 'post',
    data
  })
}
//自定义字段更新
export function updateWfCustomfield(id, data) {
  return request({
    url: `/wf/customfield/${id}/`,
    method: 'put',
    data
  })
}
//自定义字段删除
export function deleteWfCustomfield(id, data) {
  return request({
    url: `/wf/customfield/${id}/`,
    method: 'delete',
    data
  })
}
//流转列表
export function getWfTransitionList(id) {
  return request({
    url: `/wf/workflow/${id}/transitions/`,
    method: 'get'
  })
}
//流转创建
export function createWfTransition(data) {
  return request({
    url: '/wf/transition/',
    method: 'post',
    data
  })
}
//流转更新
export function updateWfTransition(id, data) {
  return request({
    url: `/wf/transition/${id}/`,
    method: 'put',
    data
  })
}
//流转删除
export function deleteWfTransition(id, data) {
  return request({
    url: `/wf/transition/${id}/`,
    method: 'delete',
    data
  })
}
//工单列表
export function getTickets(query) {
  return request({
    url: `/wf/ticket/`,
    method: 'get',
    params:query
  })
}
//新建工单
export function createTicket(data) {
  return request({
    url: '/wf/ticket/',
    method: 'post',
    data
  })
}
  //详情
export function ticketread(id) {
  return request({
    url: `/wf/ticket/${id}/`,
    method: 'get',
    
  })

}
//接单
export function ticketAccpet(id,data) {
  return request({
    url: `/wf/ticket/${id}/accpet/`,
    method: 'post',
    data
  })
}
//撤回工单，允许创建人在指定状态撤回工单至初始状态
export function ticketRetreat(id,data) {
  return request({
    url: `/wf/ticket/${id}/retreat/`,
    method: 'post',
    data
  })
}
//关闭工单，仅允许创建人在初始状态关闭工单
export function ticketAddNode(id,data) {
  return request({
    url: `/wf/ticket/${id}/add_node/`,
    method: 'post',
    data
  })
}
//加签
export function ticketClose(id,data) {
  return request({
    url: `/wf/ticket/${id}/close/`,
    method: 'post',
    data
  })
}
//加签
export function ticketAddNodeEnd(id,data) {
  return request({
    url: `/wf/ticket/${id}/add_node_end/`,
    method: 'post',
    data
  })
}
//工单删除
export function ticketDestory(data) {
  return request({
    url: `/wf/ticket/destory/`,
    method: 'post',
    data
  })
}
//工单详情
export function getTicketDetail(id) {
  return request({
    url: `/wf/ticket/${id}/`,
    method: 'get'
  })
}

//工单流转
export function getTicketTransitions(id) {
  return request({
    url: `/wf/ticket/${id}/transitions/`,
    method: 'get'
  })
}

//工单流转记录
export function getTicketFlowlog(id) {
  return request({
    url: `/wf/ticket/${id}/flowlogs/`,
    method: 'get'
  })
}
//工单代办数量
export function getCount(data) {
  return request({
    url: `/wf/ticket/duty_agg/`,
    method: 'get',
    params:data
  })
}
//工单代办数量
export function getCodes() {
  return request({
    url: `/wf/participant_from_code`,
    method: 'get'
  })
}
//工单详情
export function getWorkflowInit(id) {
  return request({
    url: `/wf/workflow/${id}/init/`,
    method: 'get'
  })
}
