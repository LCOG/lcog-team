<template>
<q-layout view="lHh Lpr lFf">
  <q-page-container>
    <q-page class="q-mt-md">
      <div id="title-row" class="row items-center q-pa-sm q-pl-md">
        <q-img
          src="../assets/summit-suite-logo.png"
          class="q-mr-sm"
          id="icon"
        />
        <div class="title col column justify-center">Public Interest Software for Governments by LCOG</div>
      </div>
      <q-img
        src="../assets/mountainbkg_right@10x.png"
      />
      <div id="hero-text" class="row items-center q-pl-xl q-pb-lg q-pr-xl">
        <div id="hero-text-container">
          <div class="hero-text-header">Simple Tools for Smoother Operations</div>
          <div class="q-pt-sm">Government teams run on processes—but too often, the software meant to support them is expensive, bloated, or just doesn’t fit. Together, we are building a collection of lightweight, modular apps designed to streamline essential tasks without unnecessary complexity.</div>
          <div class="q-pt-sm">Each app in the suite does one thing well—whether it’s managing employee transitions, reconciling credit card purchases, or automating multi-step approval processes.</div>
        </div>
      </div>

      <div class="row items-center justify-center contact-button">
        <q-btn rounded color="white" text-color="primary" @click="showContactDialog=true" class="q-py-md q-px-lg">Get Involved</q-btn>
      </div>
      
      <div id="hero-subtext" class="row items-center q-py-xl q-pa-xl">
        <div id="hero-subtext-placeholder" class="col"></div>
        <div class="col">
          <div class="hero-subtext-header">Individually powerful, better together. </div>
          <div>Smaller government agencies sometimes struggle to find a good matches with typical corporate SaaS vendors. To match the great work our government partners do, we are creating <span class="text-bold">Public-Interest Software</span>. We maximize services, not profit. We do this by keeping things simple: our apps function independently from one another, they are delightful to use, and they do just one thing well. This is Oregonians making tools for Oregonians.</div>
        </div>
      </div>

      <div class="row product items-center q-pl-md">
        <div class="q-px-lg q-pt-lg product-text-mobile">
          <div class="text-h4 q-mb-sm">Workflows</div>
          <div class="description">Handle internal processes via a customizable interface. Processes like new employee onboarding can involve many steps and decision points, and require that many different people complete them. Customizable reminders ensure that everyone has the right information at the right time. Administrative dashboards give decision makers a high-level view so nothing falls behind schedule. Web hooks allow you to integrate Workflows with your other tools.</div>
        </div>
        <div class="col q-pa-lg product-text">
          <div class="text-h4 q-mb-sm">Workflows</div>
          <div class="description">Handle internal processes via a customizable interface. Processes like new employee onboarding can involve many steps and decision points, and require that many different people complete them. Customizable reminders ensure that everyone has the right information at the right time. Administrative dashboards give decision makers a high-level view so nothing falls behind schedule. Web hooks allow you to integrate Workflows with your other tools.</div>
        </div>
        <div class="col q-pa-lg">
          <div class="row items-center justify-center">
            <q-img
              src="../assets/marketing/workflows.png"
              @click="playVideo('https://www.youtube.com/embed/uoW-xsl9Wgo?si=IYWq1RTPUQX75sDu')"
              class="cursor-pointer"
            />
          </div>
        </div>
      </div>
      
      <div class="row product product-alt items-center q-pl-md">
        <div class="q-px-lg q-pt-lg product-text-mobile">
          <div class="text-h4 q-mb-sm">Credit Card Reconciliation</div>
          <div class="description">Simplify the process of reconciling employee credit card bank statements by giving the right tools to the right people. Employees can upload receipts anytime they want. Approvers are notified and can quickly review expenses. Fiscal can quickly see which cards are held up by which people, and automated reminders mean they don't have to bug anyone.</div>
        </div>
        <div class="col q-pa-lg">
          <div class="row items-center justify-center">
            <q-img
              src="../assets/marketing/cc.png"
              @click="playVideo('https://www.youtube.com/embed/AVE43P70CgM?si=LRct-26b4byHxG29')"
              class="cursor-pointer"
            />
          </div>
        </div>
        <div class="col q-pa-lg product-text">
          <div class="text-h4 q-mb-sm">Credit Card Reconciliation</div>
          <div class="description">Simplify the process of reconciling employee credit card bank statements by giving the right tools to the right people. Employees can upload receipts anytime they want. Approvers are notified and can quickly review expenses. Fiscal can quickly see which cards are held up by which people, and automated reminders mean they don't have to bug anyone.</div>
        </div>
      </div>
      
      <div class="row product items-center q-pl-md">
        <div class="q-px-lg q-pt-lg product-text-mobile">
          <div class="text-h4 q-mb-sm">Desk Reservation</div>
          <div class="description">For hybrid work environments, reserve a desk on the way into the office. Desks can be held on specific dates or days of the week for specific people.</div>
        </div>
        <div class="col q-pa-lg product-text">
          <div class="text-h4 q-mb-sm">Desk Reservation</div>
          <div class="description">For hybrid work environments, reserve a desk on the way into the office. Desks can be held on specific dates or days of the week for specific people.</div>
        </div>
        <div class="col q-pa-lg">
          <div class="row items-center justify-center">
            <q-img
              src="../assets/marketing/deskreservation.png"
              @click="playVideo('https://www.youtube.com/embed/YT5sxPuXy78?si=wX-hNqmYPUTIfr-7')"
              class="cursor-pointer"
            />
          </div>
        </div>
      </div>

      <div class="row product product-alt items-center q-pl-md">
        <div class="q-px-lg q-pt-lg product-text-mobile">
          <div class="text-h4 q-mb-sm">Responsibilities</div>
          <div class="description">For teams that are constantly asking "Who's in charge of that thing, again?", we have a simple solution. Make notes and links to documentation, and assign backups for each role.</div>
        </div>
        <div class="col q-pa-lg">
          <div class="row items-center justify-center">
            <q-img
              src="../assets/marketing/responsibilities.png"
              @click="playVideo('https://www.youtube.com/embed/g3as8sZrDXI?si=qoVP-lMfjtjLUtAo')"
              class="cursor-pointer"
            />
          </div>
        </div>
        <div class="col q-pa-lg product-text">
          <div class="text-h4 q-mb-sm">Responsibilities</div>
          <div class="description">For teams that are constantly asking "Who's in charge of that thing, again?", we have a simple solution. Make notes and links to documentation, and assign backups for each role.</div>
        </div>
      </div>

      <div class="row product items-center q-pl-md">
        <div class="q-px-lg q-pt-lg product-text-mobile">
          <div class="text-h4 q-mb-sm">Time Off</div>
          <div class="description">On its face, just a simple time off request tool; view team time off on a shared calendar. Integrate with the Responsibilities app to automatically flag when both primary and backup for a specific role will be out of office so you can be aware of any important gaps in coverage.</div>
        </div>
        <div class="col q-pa-lg product-text">
          <div class="text-h4 q-mb-sm">Time Off</div>
          <div class="description">On its face, just a simple time off request tool; view team time off on a shared calendar. Integrate with the Responsibilities app to automatically flag when both primary and backup for a specific role will be out of office so you can be aware of any important gaps in coverage.</div>
        </div>
        <div class="col q-pa-lg">
          <div class="row items-center justify-center">
            <q-img
              src="../assets/marketing/timeoff.png"
              @click="playVideo('https://www.youtube.com/embed/sYu4pvTPKME?si=_VtbuAQesudsjlVD')"
              class="cursor-pointer"
            />
          </div>
        </div>
      </div>

      <div class="row items-center justify-center contact-button">
        <q-btn rounded color="white" text-color="primary" @click="showContactDialog=true" class="q-py-md q-px-lg">Get Involved</q-btn>
      </div>

      <!-- <div>Next - PRs</div>
      <div>Next - Government Websites</div> -->
    </q-page>

    <q-dialog v-model="showContactDialog">
      <q-card class="q-pa-lg">
        <div class="text-h5 q-mb-sm text-center">Contact Us</div>
        <div class="text-center">If you'd like to demo our tools or want to</div>
        <div class="text-center">hear more about public-interest software,</div>
        <div class="text-center">please reach out!</div>

        <q-card-section>
          <div class="row no-wrap items-center justify-center">
            <div>
              <q-avatar square class="q-mr-md">
                <q-img src="../assets/lcog-logo.png" />
              </q-avatar>
            </div>
            <div>
              <div><strong>Daniel Wilson</strong></div>
              <div>Principal Web Developer</div>
              <div><a href="mailto:dwilson@lcog-or.gov">dwilson@lcog-or.gov</a></div>
            </div>
          </div>
        </q-card-section>

        <q-card-section>
          <div class="row no-wrap items-center justify-center">
            <div>
              <q-avatar square class="q-mr-md">
                <q-img src="../assets/lcog-logo.png" />
              </q-avatar>
            </div>
            <div>
              <div><strong>Heidi Leyba</strong></div>
              <div>Chief Technology Officer</div>
              <div><a href="mailto:hleyba@lcog-or.gov">hleyba@lcog-or.gov</a></div>
            </div>
          </div>
        </q-card-section>

        <q-card-section>
          <div class="text-center">More information about Lane Council of</div>
          <div class="text-center">Governments can be found at <a href="https://lcog-or.gov">lcog-or.gov</a></div>
        </q-card-section>

      </q-card>
    </q-dialog>

    <q-dialog v-model="showVideoDialog" maximized>
      <q-video
        id="video-player"
        :src="dialogVideoUrl"
        autoplay
      />
    </q-dialog>
  </q-page-container>
</q-layout>
</template>

<style lang="scss">
body {
  font-family: 'Nunito Sans';
}

.q-header {
  display: none;
}

#title-row {
  height: 100px;

  @media screen and (max-width: 724px) {
    height: 80px;
  }

  #icon {
    height: 80px;
    width: 217.6px;

    @media screen and (max-width: 724px) {
      height: 33.33px;
      width: 90.67px;
    }
  }

  .title {
    color: #191C20;
    font-family: 'Raleway';
    font-size: 36px;
    font-style: normal;
    font-weight: 400;
    line-height: 44px; /* 122.222% */
    height: 100%;

    @media screen and (max-width: 724px) {
      font-size: 18px;
      line-height: normal;
    }
  }

}

.contact-button {
  background-color: #1D2D3A;
  padding-top: 30px;
  padding-bottom: 40px;

  button {
    font-family: 'Raleway';
    font-size: 18px;
    font-weight: 500;
  }
}

#hero-image {
  height: 150px;
}

#hero-text {
  background-color: #1D2D3A;;
  font-family: 'Raleway';
  font-size: 24px;
  color: #F8F9FF;

  #hero-text-container {
      width: 75%;
      @media screen and (max-width: 900px) {
        width: 100%;
      }

      .hero-text-header {
        color: #D2E4FF;
        font-size: 32px;
      }
  }
}

#hero-subtext {
  background-color: #F9E287;
  font-family: 'Raleway';
  font-size: 24px;
  color: #191C20;

  #hero-subtext-placeholder {
    @media screen and (max-width: 900px) {
      display: none;
    }
  }

  .hero-subtext-header {
    font-size: 32px;
  }
}

.product {
  background-color: #1D2D3A;
  color: #F8F9FF;

  .description {
    font-size: 18px;
  }

  .product-text-mobile {
    display: none;

    @media screen and (max-width: 900px) {
      display: block;
    }
  }
  .product-text {
    display: block;

    @media screen and (max-width: 900px) {
      display: none;
    }
  }
}

.product-alt {
  background-color: #B2CEE5;
  color: #191C20;
}

#video-player {
  width: 80vw;
  height: 80vh;
}

</style>

<script setup lang="ts">

import { ref } from 'vue'

let dialogVideoUrl = ref('')
let showVideoDialog = ref(false)
let showContactDialog = ref(false)

function playVideo(url: string) {
  dialogVideoUrl.value = url
  showVideoDialog.value = true
}

</script>