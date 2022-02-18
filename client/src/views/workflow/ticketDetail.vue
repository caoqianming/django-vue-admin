<template>
  <div class="app-container">
    <el-card style="margin-bottom: 10px">
      <el-steps :active="actives" spac="400px" align-center="" style="padding-top: 20px;">
        <el-step :title="item.name" v-for="item in flowSteps " :key="item.id"></el-step>
      </el-steps>
    </el-card>
    <el-row>
      <el-col :span="8">
        <el-card>
          <svg height=800 id="mySvg" style="width:100%!important;"></svg>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card style="margin-left: 10px">
          <p style="text-align: center;font-size: 20px">{{ticketDetail.title}}</p>
          <el-col :span="12">
            <div class="items">
              <span class="itemLabel">工作流：</span>
              <span>{{ticketDetail.workflow_.name}}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="items">
              <span class="itemLabel">流水号：</span>
              <span>{{ticketDetail.sn}}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="items">
              <span class="itemLabel">创建时间：</span>
              <span>{{ticketDetail.create_time}}</span>
            </div>
          </el-col>
          <el-col v-for="item in ticketDetail.ticket_data_" :key="item.id" :span="12">
            <div class="items">
              <span class="itemLabel">{{item.field_name}}：</span>
              <span>{{item.field_display}}</span>
            </div>
          </el-col>
        </el-card>
        <el-card style="margin-left: 10px">
          <el-table :data="logs" fit stripe
                    style="width: 100%;border-top:1px solid #EBEEF5;"
                    height="500"
                    highlight-current-row
          >
            <el-table-column label="工单标题" min-width="100">
              <template slot-scope="scope" v-if="scope.row.ticket_data">
                <span>{{scope.row.ticket_data.title}}中</span>
              </template>
            </el-table-column>
            <el-table-column label="进行状态" min-width="100">
              <template slot-scope="scope" v-if="scope.row.state_">
                <span v-if="scope.row.state_.type==0">{{scope.row.state_.name}}中</span>
                <span v-else>已{{scope.row.state_.name}}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作人" min-width="100">
              <template slot-scope="scope" v-if="scope.row.participant_">{{ scope.row.participant_.name }}</template>
            </el-table-column>
            <el-table-column label="操作意见" min-width="100" prop="suggestion">
            </el-table-column>
            <el-table-column label="更新时间" min-width="100" prop="update_time">
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script src="https://d3js.org/d3.v4.min.js"></script>
<script>
  import {getOrgAll} from "@/api/org";
  import {upUrl, upHeaders} from "@/api/file";
  import {getUserList} from "@/api/user";
  import {
    getWorkflowList, getWfCustomfieldList, getWfStateList, getWfTransitionList, ticketHandle
    , getWfFlowSteps, getTicketDetail, getTicketTransitions, getTicketFlowlog, ticketRetreat,
    ticketAddNode, ticketAddNodeEnd, ticketClose
  } from "@/api/workflow";
  import Pagination from "@/components/Pagination";
  import dagreD3 from 'dagre-d3'
  import * as d3 from 'd3'

  export default {
    name: "ticketDetail",
    components: {Pagination},
    inject: ['reload'],
    data() {
      return {
        step: 4,
        actives: 4,
        ticketId: 0,
        stateSteps: 0,
        ticketForm: {
          transition: '',
          ticket_data: {},
          suggestion: '',
        },
        handleType: '1',
        handleLabel: '撤回原因',
        handleTitle: '工单撤回',
        handleForm: {
          suggestion: '',
        },
        addForm: {
          toadd_user: '',
          suggestion: '',
        },
        tooltip: null,
        handleRule: {},
        upUrl: upUrl(),
        upHeaders: upHeaders(),
        userId: '',
        workflow: '',
        watchedName: '',
        watchedCreateTime: '',
        logs: [],
        orgList: [],
        staffs: [],
        edges: [],
        nodes: [],
        tooltip: [],
        fileList: [],
        workflows: [],
        flowSteps: [],
        ticketDetail: {},
        operationBtn: [],
        customfields: [],
        transitions: [],
        limitedAdd: false,
        limitedHandle: false,
        ticketFormRule: {},
      }
    },
    mounted() {
      let that = this;
      that.userId = sessionStorage.getItem('userId')
      let ticketId = that.ticketId = this.$route.params.ticketId;
      let workflow = that.workflow = this.$route.params.workflow;
      let handleTicketId = sessionStorage.getItem('handleTicketId');
      let handleTicketWorkflow = sessionStorage.getItem('handleTicketWorkflow');
      if (ticketId && workflow) {
        if (handleTicketId && handleTicketWorkflow) {
          sessionStorage.removeItem('handleTicketId');
          sessionStorage.removeItem('handleTicketWorkflow');
          sessionStorage.setItem('handleTicketId', ticketId);
          sessionStorage.setItem('handleTicketWorkflow', workflow);
        } else {
          sessionStorage.setItem('handleTicketId', ticketId);
          sessionStorage.setItem('handleTicketWorkflow', workflow);
        }
      } else {
        ticketId = that.ticketId = handleTicketId;
        workflow = that.workflow = handleTicketWorkflow;
      }
      this.getTicketFlowlogs(ticketId);
      getTicketTransitions(ticketId).then(res => {
        this.operationBtn = res.data;
      })
      getOrgAll().then((orgRes) => {
        that.orgList = orgRes.data;
        getUserList({page: 0}).then(userRes => {
          if (userRes.data) {
            that.staffs = userRes.data;
            getWfFlowSteps(ticketId).then((res) => {
              if (res.data) {
                //流程步骤数组
                that.flowSteps = res.data;
                getTicketDetail(ticketId).then((res) => {
                  if (res.data) {
                    that.tooltip = that.createTooltip();
                    that.ticketDetail = res.data;
                    for (let i = 0; i < that.ticketDetail.ticket_data_.length; i++) {
                      if (that.ticketDetail.ticket_data_[i].label === "sys_user") {
                        that.ticketDetail.ticket_data_[i].field_choice = that.staffs;
                      }
                      if (that.ticketDetail.ticket_data_[i].label === "deptSelect") {
                        that.ticketDetail.ticket_data_[i].field_choice = that.orgList;
                      }
                    }
                    // console.log(that.ticketDetail.state_.enable_retreat);
                    let state = res.data.state;
                    let dat = that.flowSteps.filter((item) => {
                      return item.id == state;
                    })
                    // debugger;
                    let state_fields = dat[0].state_fields;
                    if (state_fields !== {}) {
                      for (let labe in state_fields) {
                        for (let j = 0; j < that.ticketDetail.ticket_data_.length; j++) {
                          if (that.ticketDetail.ticket_data_[j].field_key === labe) {
                            // debugger;
                            // console.log(labe)
                            // console.log(state_fields[labe])
                            if (state_fields[labe] !== 4) {
                              that.ticketDetail.ticket_data_[j].is_hidden = false
                            } else {
                              that.ticketDetail.ticket_data_[j].is_hidden = true
                            }
                          }
                        }
                      }
                    }
                    that.sort = dat[0].sort;
                    that.actives = that.flowSteps.indexOf(dat[0]);
                    if (that.flowSteps.length - that.actives > 1) {
                    } else {
                      that.actives = that.flowSteps.length;
                    }
                    var g = new dagreD3.graphlib.Graph().setGraph({
                      rankdir: 'DL',
                      nodesep: 100,
                      edgesep: 10,//两条线之间的距离
                      ranksep: 50,//节点之间的距离
                      marginx: 60,
                      marginy: 20,
                    });
                    //获取state得到节点
                    getWfStateList(workflow).then((response) => {
                      if (response.data) {
                        let nodes = response.data;

                        // 添加节点
                        nodes.forEach((item) => {
                          if (item.sort == that.sort) {
                            g.setNode(item.id, {
                              // 节点标签
                              label: item.name,
                              // 节点形状
                              shape: 'rect',
                              toolText: item.name,
                              //节点样式
                              style: "fill:#409EFF;stroke:#000",
                              labelStyle: "fill:#000;",
                              rx: 5,//矩形节点圆角度
                              ry: 5
                            });

                          } else {
                            g.setNode(item.id, {
                              // 节点标签
                              label: item.name,
                              // 节点形状
                              shape: 'rect',
                              toolText: item.name,
                              //节点样式
                              style: "fill:#fff;stroke:#000",
                              labelStyle: "fill:#000;",
                              rx: 5,//矩形节点圆角度
                              ry: 5
                            });
                          }
                        });
                        g.nodes().forEach(function (v) {
                          console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
                        });
                        //获取流转得到线  链接关系
                        getWfTransitionList(workflow).then((res) => {
                          if (res.data) {
                            let transitionList = res.data;
                            transitionList.forEach((transitions) => {
                              let transition0 = transitions;
                              if (transition0.condition_expression.length > 0) {
                                g.setNode(transition0.source_state_.id + 100000, {
                                  label: "条件表达式",
                                  style: "fill: #a4d088",
                                  shape: "diamond"
                                });
                                g.setEdge(transition0.source_state_.id, transition0.source_state_.id + 100000, {
                                  // 边标签
                                  label: transition0.name,
                                  style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px"
                                });
                                let condition_expression = transition0.condition_expression;
                                condition_expression.forEach(condition_expression0 => {
                                  g.setEdge(transition0.source_state_.id + 100000, condition_expression0.target_state, {
                                    label: condition_expression0.label,
                                    style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px"
                                  })
                                })
                              } else {
                                g.setEdge(transition0.source_state_.id, transition0.destination_state_.id, {
                                  // 边标签
                                  label: transition0.name,
                                  // 边样式
                                  style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px" // 根据后台数据来改变连线的颜色
                                });
                              }
                            })
                            g.nodes().length - 1
                            g.nodes().forEach(function (v) {
                              console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
                            });
                            // 创建渲染器
                            let render = new dagreD3.render();
                            // 选择 svg 并添加一个g元素作为绘图容器.
                            let svg = d3.select('#mySvg');
                            let svgGroup = svg.append('g');
                            let zoom = d3.zoom()
                              .on("zoom", function () {
                                svgGroup.attr("transform", d3.event.transform);
                              });
                            svg.call(zoom);
                            // 在绘图容器上运行渲染器生成流程图.
                            render(d3.select("svg g"), g);
                            // this.getTicketFlowlogs(ticketId);
                            getTicketFlowlog(ticketId).then(res => {
                              if (res.data) {
                                that.logs = res.data;
                                svgGroup
                                  .selectAll('g.node')
                                  .on('mouseover', (v) => {
                                    // 假如当前toolText为"",则不展示
                                    //这里就是自定义tooltip的内容
                                    let filList = [], strList = [];
                                    filList = nodes.filter((ii) => {
                                      return ii.name === g.node(v).label
                                    })
                                    if (!filList.length) {
                                      return
                                    }
                                    filList.map((k) => {
                                      let filte = that.logs.filter(item => {
                                        return item.state == k.id;
                                      })
                                      //每个
                                      let str = '处理人：' + filte[0].participant_.name;
                                      strList.push(str)
                                    })
                                    that.tipVisible(strList)
                                  })
                                  .on('mouseout', () => {
                                    this.tipHidden()
                                  })
                              }
                            })

                          } else {
                          }
                        });
                      }
                    });
                  }
                });
              }
            });
          }
        })
      });
    },
    activated() {
    },
    methods: {
      getUser() {
        getUserList({}).then(res => {
          if (res.data) {
            this.staffs = res.data.results;
          }
        })
      },
      //工单流转记录
      getTicketFlowlogs(id) {
        getTicketFlowlog(id).then(res => {
          if (res.data) {
            this.logs = res.data;
          }
        })
      },
      handlePreview(file) {
        if ("url" in file) {
          window.open(file.url);
        } else {
          window.open(file.response.data.path);
        }
      },
      handleUpSuccess(res, file, filelist) {
        this.process.instruction = res.data.id;
      },
      handleRemove(file, filelist) {
        this.process.instruction = null;
      },
      // 创建提示框
      createTooltip() {
        return d3
          .select('body')
          .append('div')
          .classed('tooltip', true)
          .style('opacity', 0)
          .style('display', 'none')
      },
      // tooltip显示
      tipVisible(textContent) {
        this.tooltip
          .transition()
          .duration(400)
          .style('opacity', 1)
          .style('display', 'block')
          .style('color', '#ffffff')
          .style('z-index', '3999')
          .style('padding', '20px 30px')
          .style('border-radius', '5px')
          .style('position', 'fixed')
          .style('background', 'rgba(0,0,0,.7)')
        this.tooltip
          .html(textContent)
          .style('left', `${d3.event.pageX + 15}px`)
          .style('top', `${d3.event.pageY - 10}px`)
      },
      // tooltip隐藏
      tipHidden() {
        this.tooltip
          .transition()
          .duration(400)
          .style('opacity', 0)
          .style('display', 'none')
      },
      operationSubmit(id) {
        this.ticketForm.transition = id;
        this.ticketForm.ticket_data = this.ticketDetail.ticket_data;
        let obj = new Object();
        obj.transition = id;
        obj.ticket_data = this.ticketDetail.ticket_data;
        obj.suggestion = this.ticketForm.suggestion;
        // console.log(this.ticketForm);
        ticketHandle(this.ticketId, obj).then(res => {
          if (res.data) {
            this.$store.dispatch("user/getCount", {})
            this.$router.replace({name: "ticket"})
          }
        })
      },
      retreatCancel() {
        this.limitedHandle = false;
      },
      handleSubmit() {
        let text = '', url = '';
        if (this.handleType === '1') {
          text = "确认撤回工单吗?";
          url = ticketRetreat;
        } else if (this.handleType === '2') {
          text = "确认关闭工单吗?";
          url = ticketClose;
        }
        if (this.handleType === '3') {
          text = "确认处理工单吗?";
          url = ticketAddNodeEnd;
        }
        this.$confirm(text, "温馨提示", {
          confirmButtonText: "确认",
          cancelButtonText: "取消",
          type: "warning",
        })
          .then(async () => {
            url(this.ticketId, this.handleForm).then(res => {
              this.limitedHandle = false;
              this.$store.dispatch("user/getCount", {})
              this.$router.replace({name: "ticket"})
              this.$message.success("成功");
            })
          })
          .catch((err) => {
            console.error(err);
          });
      },
      handleClick(index) {
        this.limitedHandle = true;
        this.handleType = index;
        if (index === '1') {
          this.handleTitle = '工单撤回';
          this.handleLabel = '撤回原因';
        } else if (index === '2') {
          this.handleTitle = '工单关闭';
          this.handleLabel = '关闭原因';
        } else if (index === '3') {
          this.handleTitle = '加签处理';
          this.handleLabel = '加签意见';
        }
      },
      handleAdd() {
        this.getUser();
        this.limitedAdd = true;
      },
      addCancel() {
        this.limitedAdd = false;
      },
      addSubmit() {
        ticketAddNode(this.ticketId, this.addForm).then(res => {
          if (res.data) {
            this.limitedAdd = false;
            this.$nextTick(function () {
              this.limitedAdd = true;
              this.$store.dispatch("user/getCount", {})
              this.$router.replace({name: "ticket"})
            })

          }
        })
      },
    }
  }
</script>
<style scoped>
  .svgWrapper {
    background: #fff;
    width: 800px;
    margin: 10vh auto 0;
    text-align: center;
    border-radius: 2px;
  }

  .svgItem {
    padding: 20px 40px 0;
    font-family: Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB, Microsoft YaHei, Arial, sans-serif;
    font-size: 18px;
    display: flex;
    justify-content: space-between;
  }

  svg {
    font-size: 14px;
  }

  .node rect {
    stroke: #606266;
    fill: #fff;
  }

  .edgePath path {
    stroke: #606266;
    fill: #333;
    stroke-width: 1.5px;
  }

  .el-icon-close {
    cursor: pointer;
  }

  .listItem {
    margin-top: 15px;
    font-size: 16px;
  }

  .listItem > span {
    width: 100px;
    text-align: right;
    margin-right: 10px;
    display: inline-block;
  }

  .items {
    height: 35px;
    line-height: 35px;
    padding-left: 20px;
  }

  .itemLabel {
    font-size: 14px;
    color: #606266;
    font-weight: 600;
  }
</style>
