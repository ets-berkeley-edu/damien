<template>
  <div class="align-center d-flex flex-wrap justify-space-between pb-3">
    <h1 id="page-title" class="mr-2" tabindex="-1">
      <slot />
    </h1>
    <div class="ml-auto">
      <slot name="append" />
    </div>
  </div>
</template>
