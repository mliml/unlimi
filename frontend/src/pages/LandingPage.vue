<template>
  <div class="bg-bg min-h-screen">
    <LandingNav />

    <!-- Hero Section -->
    <section>
      <HeroSection />
    </section>

    <!-- Features Section -->
    <section class="pb-12">
      <FeaturesSection />
    </section>

    <LandingFooter />
  </div>
</template>

<script setup>
import LandingNav from '@/components/landing/LandingNav.vue'
import HeroSection from '@/components/landing/HeroSection.vue'
import FeaturesSection from '@/components/landing/FeaturesSection.vue'
import LandingFooter from '@/components/landing/LandingFooter.vue'
</script>
