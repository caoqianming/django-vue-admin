<template>
  <div class="app-container">
        <div>
          <el-select
            v-model="listQuery.type"
            placeholder="文件类型"
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
            placeholder="文件名"
            style="width: 300px;"
            class="filter-item"
            @keyup.enter.native="handleFilter"
          />
          <el-button
            class="filter-item"
            type="primary"
            icon="el-icon-search"
            @click="handleFilter"
            size="small"
          >搜索</el-button>
          <el-button
            class="filter-item"
            type="primary"
            icon="el-icon-refresh-left"
            @click="resetFilter"
            size="small"
          >重置</el-button>
        </div>
        <el-table
          v-loading="listLoading"
          :data="fileList.results"
          style="width: 100%;margin-top:10px;"
          border
          fit
          stripe
          highlight-current-row
          max-height="600"
        >
          <el-table-column type="index" width="50" />
          <el-table-column align="center" label="名称">
            <template slot-scope="scope">
                <el-link type="primary" :href="scope.row.file" target="_blank">{{ scope.row.name }}</el-link>
            </template>
          </el-table-column>
          <el-table-column align="header-center" label="类型">
            <template slot-scope="scope">{{ scope.row.type }}</template>
          </el-table-column>
          <el-table-column align="header-center" label="格式">
            <template slot-scope="scope">{{ scope.row.mime }}</template>
          </el-table-column>
          <el-table-column align="header-center" label="大小(B)">
            <template slot-scope="scope">{{ scope.row.size }}</template>
          </el-table-column>
          <el-table-column align="header-center" label="地址">
            <template slot-scope="scope">{{ scope.row.path }}</template>
          </el-table-column>
          <el-table-column label="上传日期">
            <template slot-scope="scope">
              <span>{{ scope.row.create_time }}</span>
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="fileList.count>0"
          :total="fileList.count"
          :page.sync="listQuery.page"
          :limit.sync="listQuery.page_size"
          @pagination="getList"
        />
  </div>
</template>
<script>
import { getFileList } from "@/api/file"
import Pagination from "@/components/Pagination"
export default {
  components: { Pagination },
  data() {
    return {
      fileList: {count:0},
      listLoading: true,
      listQuery: {
        page: 1,
        page_size: 20
      },
      enabledOptions: [
        { key: "文档", display_name: "文档" },
        { key: "图片", display_name: "图片" },
        { key: "音频", display_name: "音频" },
        { key: "视频", display_name: "视频" },
        { key: "其它", display_name: "其它" }
      ],
    };
  },
  created() {
    this.getList();
  },
  methods: {
    getList() {
      this.listLoading = true;
      getFileList(this.listQuery).then(response => {
        if (response.data) {
          this.fileList = response.data
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
