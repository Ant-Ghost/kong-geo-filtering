<template>
  <div>
    <a-space direction="horizontal">
      <a-switch v-model:checked="checkState">
        <template #checkedChildren><check-outlined /></template>
        <template #unCheckedChildren><close-outlined /></template>
      </a-switch>
      <div>
        <div v-if="checkState">
          <p style="font-weight: bold; color: #1677ff">Geo country Access</p>
        </div>
        <div v-else>
          <p style="font-weight: bold">Geo country Access</p>
        </div>
      </div>
      <br />
    </a-space>
    <div>
      <p v-if="checkState" style="margin: 0">
        Specify the countries to be blacklisted or whitelisted.
      </p>
    </div>
  </div>
  <div style="margin-top: 1.5em">
    <a-form
      v-if="checkState"
      :model="formState"
      :label-col="labelCol"
      :wrapper-col="wrapperCol"
    >
      <a-form-item>
        <p style="font-weight: bold; color: #1677ff; margin: 0">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            style="margin-bottom: 0"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="icon icon-tabler icons-tabler-outline icon-tabler-edit"
          >
            <path stroke="none" d="M0 0h24v24H0z" fill="none" />
            <path
              d="M7 7h-1a2 2 0 0 0 -2 2v9a2 2 0 0 0 2 2h9a2 2 0 0 0 2 -2v-1"
            />
            <path
              d="M20.385 6.585a2.1 2.1 0 0 0 -2.97 -2.97l-8.415 8.385v3h3l8.385 -8.415z"
            />
            <path d="M16 5l3 3" />
          </svg>
          Mode
        </p>
        <a-select
          v-model:value="formState.mode"
          placeholder="please select your zone"
        >
          <a-select-option value="blacklist"
            >Blacklist Countries</a-select-option
          >
          <a-select-option value="whitelist"
            >Whitelist Countries</a-select-option
          >
        </a-select>
      </a-form-item>
      <a-form-item>
        <p v-if="formState.mode == 'blacklist'" style="margin: 0">
          Add countries to your blocklist
        </p>
        <p v-else style="margin: 0">Add countries to your whitelist</p>
        <a-select
          v-model:value="formState.countries"
          mode="tags"
          :options="options"
        ></a-select>
      </a-form-item>
      <a-form-item>
        <a-button type="primary" @click="onSubmit">Save</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>
<script setup>
import { reactive, toRaw, ref } from "vue";
import { CheckOutlined, CloseOutlined } from "@ant-design/icons-vue";
import axios from "axios";
import countries from "../../countries.json";
import { toast } from "vue3-toastify";
import "vue3-toastify/dist/index.css";

let checkState = ref(false);

const formState = reactive({
  mode: "blacklist",
  countries: [],
});

const options = [];

for (let _c of countries) {
  options.push({ value: _c.code, label: _c.name });
}

const onSubmit = async () => {
  const formDetails = toRaw(formState);

  try {
    const response = await axios({
      method: "PATCH",
      url: `${process.env.VUE_APP_API_URL}/restriction/${formDetails.mode}`,
      data: {
        valid_list: formDetails.countries,
      },
    });

    if (response.status < 300) {
      toast.success("Successfully Updated");
    } else {
      toast.error("Bad Request");
      console.log(response);
    }
  } catch (err) {
    console.log(err);

    toast.error("Bad Request");
  }
};

const labelCol = { style: { width: "150px" } };
const wrapperCol = { span: 14 };
</script>

<style>
.boldBlue {
  color: "#1677ff";
  font-weight: bold;
}
</style>
