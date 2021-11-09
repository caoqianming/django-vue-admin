<template>
  <div class="app-container">
    <el-row :gutter="12">
      <el-col :span="8">
        <el-card>
          <div slot="header" class="clearfix">
            <span>CPU</span>
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item>
              <template slot="label"> 逻辑核心数 </template>
              {{ cpuData.count }}
            </el-descriptions-item>
            <el-descriptions-item>
              <template slot="label"> 物理核心数 </template>
              {{ cpuData.lcount }}
            </el-descriptions-item>
            <el-descriptions-item>
              <template slot="label"> 当前使用率 </template>
              {{ cpuData.percent }}%
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header" class="clearfix">
            <span>内存</span>
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item>
              <template slot="label"> 总内存 </template>
              {{ memoryData.total }}GB
            </el-descriptions-item>
            <el-descriptions-item>
              <template slot="label"> 已用内存 </template>
              {{ memoryData.used }}GB
            </el-descriptions-item>
            <el-descriptions-item>
              <template slot="label"> 当前使用率 </template>
              {{ memoryData.percent }}%
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div slot="header" class="clearfix">
            <span>硬盘</span>
          </div>
          <el-descriptions :column="1" border>
            <el-descriptions-item>
              <template slot="label"> 总大小 </template>
              {{ diskData.total }}GB
            </el-descriptions-item>
            <el-descriptions-item>
              <template slot="label"> 已用内存 </template>
              {{ diskData.used }}GB
            </el-descriptions-item>
            <el-descriptions-item>
              <template slot="label"> 当前使用率 </template>
              {{ diskData.percent }}%
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 2px">
      <div slot="header" class="clearfix">
        <span>日志列表</span>
      </div>
      <div>
        <el-input
          v-model="listQuery.name"
          placeholder="日志名称"
          style="width: 300px"
          class="filter-item"
          @keyup.enter.native="handleFilter"
        />
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="handleFilter"
          >搜索
        </el-button>
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-refresh-left"
          @click="resetFilter"
          >重置
        </el-button>
      </div>
      <el-table
        :data="tableData"
        style="width: 100%"
        height="100"
        v-el-height-adaptive-table="{ bottomOffset: 30 }"
      >
        <el-table-column prop="name" label="日志名称"> </el-table-column>
        <el-table-column prop="size" label="日志大小"> </el-table-column>
        <el-table-column fixed="right" label="操作" width="100">
          <template slot-scope="scope">
            <el-button @click="handleClick(scope.row)" type="text" size="small"
              >查看详情</el-button
            >
          </template>
        </el-table-column>
      </el-table>
      <el-dialog :visible.sync="dialogVisible" width="80%" title="日志详情">
        <div v-html="logdec" class="dialogDiv"></div>
      </el-dialog>
    </el-card>
  </div>
</template>


<script>
import { getlogList, getLog, getServerList } from "@/api/moritor";

const defaultCMA = {};
export default {
  components: {},
  data() {
    return {
      tableData: [],
      cpuData: [],
      diskData: [],
      memoryData: [],
      dialogVisible: false,
      logdec: "",
      text: "",
      listQuery: {},
    };
  },
  computed: {},
  watch: {},
  created() {
    this.getlogList();
    this.getServerList();
  },
  methods: {
    getlogList() {
      getlogList(this.listQuery).then((response) => {
        if (response.data) {
          this.tableData = response.data;
        }
      });
    },
    handleFilter() {
      this.getlogList();
    },
    resetFilter() {
      this.getlogList();
    },
    getServerList() {
      getServerList().then((response) => {
        if (response.data) {
          this.cpuData = response.data.cpu;
          this.diskData = response.data.disk;
          this.memoryData = response.data.memory;
        }
      });
    },
    handleClick(row) {
      this.dialogVisible = true;
      getLog(row.name).then((response) => {
        if (response.data) {
          this.logdec = response.data.replace(/\n/gm, "<br/>");
        }
      });
    },
  },
};
</script>