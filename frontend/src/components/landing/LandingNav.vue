<template>
  <nav>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div class="flex items-center justify-between">
        <!-- Brand -->
        <div class="text-2xl font-serif font-bold text-primary">
          UnLimi
        </div>

        <!-- Right buttons -->
        <div class="flex items-center space-x-4">
          <button
            @click="$router.push('/auth/login')"
            class="px-6 py-2.5 text-sm font-medium text-textMain border border-gray-300 rounded-full hover:bg-gray-50 transition-colors"
          >
            Log In
          </button>
          <a
            href="mailto:unilimi@mliml.com"
            class="px-6 py-2.5 text-sm font-medium bg-black text-white rounded-full hover:bg-gray-800 transition-colors"
          >
            Get Touch
          </a>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
// No imports needed
</script>
