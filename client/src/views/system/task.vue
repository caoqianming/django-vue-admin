<template>
  <div class="app-container">
        <div>
          <el-select
            v-model="listQuery.enabled"
            placeholder="是否启用"
            clearable
            style="width: 200px"
            class="filter-item"
            @change="handleFilter"
          >
            <el-option
              v-for="item in enabledOptions"
              :key="item.key"
              :label="item.display_name"
              :value="item.key"
            />
          </el-select>
          <el-input
            v-model="listQuery.search"
            placeholder="任务名"
            style="width: 300px;"
            class="filter-item"
            @keyup.enter.native="handleFilter"
          />
          <el-button
            class="filter-item"
            type="primary"
            icon="el-icon-search"
            @click="handleFilter"
          >搜索</el-button>
          <el-button
            class="filter-item"
            type="primary"
            icon="el-icon-refresh-left"
            @click="resetFilter"
          >重置</el-button>
        </div>
        <el-table
          v-loading="listLoading"
          :data="dataList.results"
          style="width: 100%;margin-top:10px;"
          border
          fit
          stripe
          highlight-current-row
          max-height="600"
        >
          <el-table-column type="index" width="50" />
          <el-table-column align="center" label="名称">
            <template slot-scope="scope">{{ scope.row.name }}
            </template>
          </el-table-column>
          <el-table-column align="header-center" label="描述">
            <template slot-scope="scope">{{ scope.row.description }}</template>
          </el-table-column>
          <el-table-column align="header-center" label="执行次数">
            <template slot-scope="scope">{{ scope.row.total_run_count }}</template>
          </el-table-column>
          <el-table-column align="header-center" label="最后执行时间">
            <template slot-scope="scope">{{ scope.row.last_run_at }}</template>
          </el-table-column>
          <el-table-column label="是否启用">
            <template slot-scope="scope">
              <span>{{ scope.row.enabled }}</span>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="dataList.count>0"
          :total="dataList.count"
          :page.sync="listQuery.page"
          :limit.sync="listQuery.page_size"
          @pagination="getList"
        />
  </div>
</template>
<script>
import { getTaskList } from "@/api/task"
import Pagination from "@/components/Pagination"
export default {
  components: { Pagination },
  data() {
    return {
      dataList: {count:0},
      listLoading: true,
      listQuery: {
        page: 1,
        page_size: 20
      },
      enabledOptions: [
        { key: "true", display_name: "启用" },
        { key: "false", display_name: "禁用" },
      ],
    };
  },
  created() {
    this.getList();
  },
  methods: {
    getList() {
      this.listLoading = true;
      getTaskList(this.listQuery).then(response => {
        if (response.data) {
          this.dataList = response.data
        }
        this.listLoading = false;
      });
    },
    resetFilter() {
      this.listQuery = {
        page: 1,
        page_size: 20
      };
      this.getList();
    },
    handleFilter() {
      this.listQuery.page = 1;
      this.getList();
    },
  }
};
</script>
