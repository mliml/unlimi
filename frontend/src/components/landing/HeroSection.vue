<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
    <div class="text-center">
      <!-- Hero Title -->
      <h1 class="text-5xl sm:text-6xl lg:text-7xl font-serif font-bold text-textMain leading-tight mb-4">
        Always Here,<br />
        Always remembering you.
      </h1>

      <!-- Subtitle -->
      <p class="text-lg sm:text-xl text-textSub max-w-3xl mx-auto mb-8">
        Unlimi: An AI therapist with persistent memory and switchable therapy styles.
      </p>

      <!-- CTA Button -->
      <button
        @click="$router.push('/auth/register')"
        class="inline-block px-10 py-4 text-base font-semibold
               bg-black text-white rounded-full
               hover:bg-gray-800 transform hover:scale-105
               transition-all duration-200
               shadow-lg hover:shadow-xl mb-6"
      >
        Get Started
      </button>

      <!-- Invite code notice -->
      <p class="text-sm text-textSub">
        The product currently requires an invite code to access.
      </p>
    </div>
  </div>
</template>

<script setup>
// No imports needed
</script>
