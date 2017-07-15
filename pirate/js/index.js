(function(window, document, $) {
  "use strict";

  var s = Snap.select("#the-pirate-scene"),
    pirate = s.select("#the-pirate"),
    head = s.select("#the-head"),
    teethBottom = s.select("#bottom-teeth"),
    mouth = s.select("#mouth-background"),
    beard = s.select("#beard"),
    torso = s.select("#torso"),
    legsGreen = s.select("#main-green"),
    legsAccentGreen = s.select("#boot-darkaccent"),
    pegLeg = s.select("#peg-leg"),
    bootLeg = s.select("#boot-leg"),
    bird = s.select("#the-bird"),
    birdBody = s.select("#bird-body");

  var theApp = {
      init: function() {
        theBird.controls();
        thePirate.controls();
      }
    },

    theBird = {
      controls: function() {
        setTimeout(function() {
          window.requestAnimationFrame(theBird.jump('20'));
        }, 1000);
        setTimeout(function() {
          window.requestAnimationFrame(theBird.jump('20'));
        }, 1650);

        setTimeout(function() {
          window.requestAnimationFrame(theBird.flapWings);
        }, 1070);
        setTimeout(function() {
          window.requestAnimationFrame(theBird.flapWings);
        }, 1800);

        setInterval(function() {
          setTimeout(function() {
            window.requestAnimationFrame(theBird.jump('20'));
          }, 1000);
          setTimeout(function() {
            window.requestAnimationFrame(theBird.flapWings);
          }, 1070);
          setTimeout(function() {
            window.requestAnimationFrame(theBird.jump('20'));
          }, 1650);
          setTimeout(function() {
            window.requestAnimationFrame(theBird.flapWings);
          }, 1800);
        }, 3000);
      },
      flapWings: function() {
        birdBody.animate({
          d: "M335,159.395h-13v-5h-10.666v5H320l1.666,4.667 h-5l-1,29.667h-4.332v6h-19.668v4.667l-13.035,0.202l-1.797,22.32c-1.897-1.094,14.518,1.511,13.417,2.979l0.032-12.378 l-0.616-1.85l0.833,2.5l-0.999,1.5l0.999,4.061h1.834l-0.668,6.334h5l-0.332,10H302v5.333h3.5v13.667h6.5v-4h4.334v-5l-5-0.334 v-4.666l10.332,0.333v13.667H327v-4h4.666v-4.667H327v-5h3.334v-4.667H337v-6h5v-5.333h19v-4l0.584-3.478l0.834,2.088l-0.5,4.996 l9.832,0.895c0,0,0.59-12.867,0.258-11.533l-1.258-12.342l-6.875,0.708l-2.209,1.667H346v-1.667h-3.666v-6h-4.668v-5.333h-6.332 v-5.667H342v3.667l9.666,0.667v5h4.668v-14.667h-4.668v-18.667l-6-0.667v-5.333L335,159.395z"
        }, 70, mina.linear, function() {
          setTimeout(function() {
            birdBody.animate({
              d: "M335,159.395h-13v-5h-10.666v5H320l1.666,4.667 h-5l-1,29.667h-4.332v6h-19.668v4.667h-10v-4.667c0,0-4.666-1-5.666,0.333v14.334h4.666v5.332H286v4h6.334l-0.668,6.334h5 l-0.332,10H302v5.333h3.5v13.667h6.5v-4h4.334v-5l-5-0.334v-4.666l10.332,0.333v13.667H327v-4h4.666v-4.667H327v-5h3.334v-4.667 H337v-6h5v-5.333h19v-4l6-0.333v-4.667h4.666v-20.667c0,0-4.334-1.333-4.666,0l-0.334,4.667h-5v4H346v-1.667h-3.666v-6h-4.668 v-5.333h-6.332v-5.667H342v3.667l9.666,0.667v5h4.668v-14.667h-4.668v-18.667l-6-0.667v-5.333L335,159.395z"
            }, 70, mina.linear);
          }, 100);
        });
      },
      jump: function(y) {
        bird.animate({
          transform: 't0,-' + y
        }, 100, mina.linear, function() {
          bird.animate({
            transform: 't0,0'
          }, 100, mina.backout);
        });
      }
    },

    thePirate = {
      controls: function() {
        window.requestAnimationFrame(thePirate.headBob);
        window.requestAnimationFrame(thePirate.bodySize);

        setTimeout(function() {
          window.requestAnimationFrame(thePirate.jump);
          window.requestAnimationFrame(thePirate.mouthOpen);
          window.requestAnimationFrame(thePirate.legKicks);
          window.requestAnimationFrame(theBird.jump('10'));
        }, 50);

        setTimeout(function() {
          window.requestAnimationFrame(thePirate.headBob);
        }, 450);

        setTimeout(function() {
          window.requestAnimationFrame(thePirate.jump);
          window.requestAnimationFrame(thePirate.mouthOpen);
          window.requestAnimationFrame(thePirate.legKicks);

          window.requestAnimationFrame(theBird.jump('10'));
        }, 500);

        setInterval(function() {
          window.requestAnimationFrame(thePirate.headBob);
          window.requestAnimationFrame(thePirate.bodySize);

          setTimeout(function() {
            window.requestAnimationFrame(thePirate.jump);
            window.requestAnimationFrame(thePirate.mouthOpen);
            window.requestAnimationFrame(thePirate.legKicks);

            window.requestAnimationFrame(theBird.jump('10'));
          }, 50);

          setTimeout(function() {
            window.requestAnimationFrame(thePirate.headBob);
          }, 450);

          setTimeout(function() {
            window.requestAnimationFrame(thePirate.jump);
            window.requestAnimationFrame(thePirate.mouthOpen);
            window.requestAnimationFrame(thePirate.legKicks);

            window.requestAnimationFrame(theBird.jump('10'));
          }, 500);
        }, 3000);

      },
      headBob: function() {
        head.animate({
          transform: 't3,-3'
        }, 50, mina.linear, function() {
          head.animate({
            transform: 't0,0'
          }, 50, mina.linear);
        });

      },
      jump: function() {
        pirate.animate({
          transform: 't0,-10'
        }, 100, mina.linear, function() {
          pirate.animate({
            transform: 't0,0'
          }, 100, mina.linear);
        });
      },
      mouthOpen: function() {
        teethBottom.animate({
          transform: 't0,12'
        }, 50, mina.linear, function() {
          setTimeout(function() {
            teethBottom.animate({
              transform: 't0,0'
            }, 50, mina.linear);
          }, 550);
        })

      },
      bodySize: function() {
        torso.animate({
          transform: 't0,3'
        }, 50, mina.linear, function() {
          torso.animate({
            transform: 't0,0'
          }, 50, mina.linear);
        });
      },
      legKicks: function() {
        legsGreen.animate({
          points: "193,354.396 183.75,383.875 190.625,389.145 213.25,396.75 230.375,377.25 248.5,377.896 250.062,380.75 256.5,387.125 268.002,396 313.625,388.414 312.821,383.582 316.375,383.125 316.375,373.873 313,372.5 308,354.396"
        }, 100, mina.linear, function() {
          legsGreen.animate({
            points: "193,354.396 193,388.396 199,394.396 229,394.396 236,377.896 248.5,377.896 245,382.896 245,389.896 252,391.396 306.5,390.896 306.5,384.396 311,384.396 311,374.396 308,374.396 308,354.396"
          }, 100, mina.linear);
        });

        legsAccentGreen.animate({
          points: "289.67,356.396 293.5,366.5 295.625,368.875 297.668,376.5 294.5,379.125 296.75,387.928 301.532,422.421 311,421.398 309.021,404.802 312.082,405.25 318.802,403.966 313.5,387.662 316.375,383.125 316.375,373.873 309.5,353.434 288.5,354.396"
        }, 100, mina.linear, function() {
          legsAccentGreen.animate({
            points: "288.5,356.896 288.5,368.896 292.5,368.896 292.5,376.396 288.5,376.396 288.5,389.396 292.5,423.396 298.5,423.396 298.5,409.896 303,409.396 308.5,404.896 308.5,384.896 311.5,384.896 311.5,374.896 309.5,353.434 288.5,354.396"
          }, 100, mina.linear);
        });

        pegLeg.animate({
          transform: 'r5,250,250'
        }, 100, mina.linear, function() {
          pegLeg.animate({
            transform: 'r0,0,0'
          }, 100, mina.linear);
        });

        bootLeg.animate({
          transform: 'r-5,250,250'
        }, 100, mina.linear, function() {
          bootLeg.animate({
            transform: 'r0,0,0'
          }, 100, mina.linear);
        });

      }
    };
  $(document).ready(function() {
    theApp.init();
  });
}(this, this.document, this.jQuery));