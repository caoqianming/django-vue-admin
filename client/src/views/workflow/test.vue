<template>
    <div id="container" style="border: 1px solid #000000;">
        <svg width="900" height="1500">
            <g />
            <rect />
        </svg>
    </div>
</template>
<script src="https://d3js.org/d3.v4.min.js"></script>
<script>
    import dagreD3 from "dagre-d3";
    import * as d3 from "d3";
    export default {
        data() {
            return {
              nodes: [
                {
                  id: "2",
                  label: "开始",
                  shape: "rect"
                },
                {
                  id: "3",
                  label: "部门领导审批",
                  shape: "diamond"
                },
                {
                  id: "4",
                  label: "综合办公室审批",
                  shape: "diamond"
                },
                {
                  id: "5",
                  label: "结束",
                  shape: "rect"
                },
              ],
              edges: [
                {
                  source: "2",
                  target: "3",
                  label: ""
                },
                {
                  source: "3",
                  target: "4",
                  label: "同意"
                },
                {
                  source: "4",
                  target: "5",
                  label: "同意"
                },
              ]
            };
        },
        mounted() {
            //获取D3
            var g = new dagreD3.graphlib.Graph().setGraph({
                align: 'DL',
                nodesep: 100,
                edgesep: 100,
                ranksep: 50,
                marginx: 50,
                marginy: 100,
            });
          console.log(g);
          // 添加节点
          this.nodes.forEach((item) => {
            g.setNode(item.id, {
              // 节点标签
              label: item.label,
              // 节点形状
              shape: item.shape,
              toolText: item.label,
              //节点样式
              style: "fill:#fff;stroke:#000",
              // 节点样式
              labelStyle: "fill:#000;",
              width: 83,
              height: 40,
              rx :5,
              ry :5
            });
          });
          // 链接关系
          this.edges.forEach(item => {
            g.setEdge(item.source, item.target, {
              // 边标签
              label: item.label,
              // 边样式
              style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px" // 根据后台数据来改变连线的颜色
            });
          });
          g.nodes().forEach(function (v) {
            console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
          });
          g.edges().forEach(function (e) {
            console.log("Edge " + e.v + " -> " + e.w + ": " + JSON.stringify(g.edge(e)));
          });
          // 创建渲染器
          let render = new dagreD3.render();
          // 选择 svg 并添加一个g元素作为绘图容器.
          let svg = d3.select('svg');
          let svgGroup = svg.select('g');
          // 在绘图容器上运行渲染器生成流程图.
          render(d3.select("svg g"), g);
        }
    };
</script>

<style scoped>
    svg {
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
    #__SVG_SPRITE_NODE__{
      position: absolute!important;
      width: 689px!important;
      height: 800px!important;
      left: 300px!important;
      top: 331px!important;
    }
</style>
