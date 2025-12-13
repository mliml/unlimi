<template>
  <div class="bg-bg min-h-screen">
    <!-- Navigation -->
    <nav>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <!-- Brand -->
          <div class="text-2xl font-serif font-bold text-primary">
            UnLimi
          </div>

          <!-- Right buttons -->
          <div class="flex items-center space-x-4">
            <a
              href="/auth/login"
              class="px-6 py-2.5 text-sm font-medium text-textMain border border-gray-300 rounded-full hover:bg-gray-50 transition-colors"
            >
              Log In
            </a>
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

    <!-- Hero Section -->
    <section>
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
          <a
            href="/auth/register"
            class="inline-block px-10 py-4 text-base font-semibold
                   bg-black text-white rounded-full
                   hover:bg-gray-800 transform hover:scale-105
                   transition-all duration-200
                   shadow-lg hover:shadow-xl mb-6"
          >
            Get Started
          </a>

          <!-- Invite code notice -->
          <p class="text-sm text-textSub">
            The product currently requires an invite code to access.
          </p>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="pb-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Section Title -->
        <div class="text-center mb-8">
          <h2 class="text-3xl sm:text-4xl font-serif font-bold text-textMain">
            Feature List
          </h2>
        </div>

        <!-- Features Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8">
          <!-- Card 1 - Primary Color -->
          <div class="bg-[#E07A5F] rounded-xl p-8">
            <h3 class="text-2xl font-serif font-semibold text-white mb-4">
              Feature Title 1
            </h3>
            <p class="text-base text-white leading-relaxed">
              Feature description placeholder text. This will be replaced with actual feature content.
            </p>
          </div>

          <!-- Card 2 - Secondary Color -->
          <div class="bg-[#5F7470] rounded-xl p-8">
            <h3 class="text-2xl font-serif font-semibold text-white mb-4">
              Feature Title 2
            </h3>
            <p class="text-base text-white leading-relaxed">
              Feature description placeholder text. This will be replaced with actual feature content.
            </p>
          </div>

          <!-- Card 3 - Tertiary Color -->
          <div class="bg-[#D4A373] rounded-xl p-8">
            <h3 class="text-2xl font-serif font-semibold text-white mb-4">
              Feature Title 3
            </h3>
            <p class="text-base text-white leading-relaxed">
              Feature description placeholder text. This will be replaced with actual feature content.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-bg py-8 mt-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-start space-x-6">
          <a
            href="#"
            class="text-sm text-textSub hover:text-primary transition-colors"
          >
            Privacy Policy
          </a>
          <span class="text-gray-300">·</span>
          <a
            href="#"
            class="text-sm text-textSub hover:text-primary transition-colors"
          >
            Terms of Use
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
// No imports needed - all content is inline
</script>
