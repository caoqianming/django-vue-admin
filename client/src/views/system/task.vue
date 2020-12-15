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
        <div style="margin-top:6px">
          <el-button type="primary" icon="el-icon-plus" @click="handleCreate" v-if="checkPermission(['task_create'])" size="small">新增</el-button>
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
        <el-dialog :visible.sync="dialogVisible" :title="dialogType==='update'?'编辑':'新增'">
      <el-form ref="Form" :model="task" label-width="80px" :rules="rule1">
        <el-form-item label="名称" prop="name">
          <el-input v-model="task.name" placeholder="名称" />
        </el-form-item>
        <el-form-item label="执行代码" prop="task">
          <el-select v-model="task.taskcode" placeholder="请选择" style="width:100%">
    <el-option
      v-for="item in taskcodoptions"
      :key="item"
      :label="item"
      :value="item">
    </el-option>
  </el-select>
        </el-form-item>
        <el-form-item label="时间策略" prop="schedule">
          <el-radio-group v-model="task.timetype">
          <el-radio :label="1">间隔</el-radio>
          <el-radio :label="2">Contab</el-radio>
        </el-radio-group>
        </el-form-item>
        <el-form-item label="每隔" prop="schedule" v-if="task.timetype==1">
          <el-input-number v-model="task.interval_number" :min="1" ></el-input-number>
          <el-select v-model="task.interval_period" placeholder="请选择" style="width:100px">
    <el-option
      v-for="item in periodOptions"
      :key="item.value"
      :label="item.label"
      :value="item.value">
    </el-option>
  </el-select>
        </el-form-item>
      </el-form>
      <div style="text-align:right;">
        <el-button type="danger" @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="confirmForm('Form')">确认</el-button>
      </div>
    </el-dialog>
  </div>
  
</template>
<script>
import { getTaskList, getTaskcodeAll } from "@/api/task"
import Pagination from "@/components/Pagination"
import checkPermission from '@/utils/permission'
const defaulttask = {
  timetype:1,
  interval_number: 1,
  interval_period:'分钟'
}
export default {
  components: { Pagination },
  data() {
    return {
      dialogVisible: false,
      dialogType:'create',
      task: defaulttask,
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
      rules1:[],
      periodOptions: [{
          value: 'days',
          label: '天'
        }, {
          value: 'hours',
          label: '小时'
        }, {
          value: 'minutes',
          label: '分钟'
        }, {
          value: 'seconds',
          label: '秒'
        }],
        taskcodoptions:[],
    };
  },
  created() {
    this.getList();
    this.getTaskcodeAll();
  },
  methods: {
    checkPermission,
    getTaskcodeAll(){
      getTaskcodeAll().then(res=>{
        this.taskcodoptions = res.data
      })
    },
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
    handleCreate(){
      this.task = Object.assign({}, defaulttask)
      this.dialogType = 'create'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['Form'].clearValidate()
      })
    },
    confirmForm() {

    }
  }
};
</script>
