; straight waveguide with a point source in the middle

(define-param eps 12)	; dielectric constant of waveguide
(define-param w 1.2)	; width of waveguide
(define-param r 0.3)  ; 

(define-param sx 1) ; size of cell parallel to wvg.
(define-param sy 8) ; size of cell perp. to wvg.
(define-param dpml 1)	; pml thickness (y-dir only!)

; set up unit cell - repeating in x-direction
(set! geometry-lattice (make lattice (size sx sy no-size)))

; construct waveguide
(set! geometry (append (list 

      (make block(center 0 0) (size infinity w infinity) 
        (material (make dielectric (epsilon eps)))))
      
        (geometric-object-duplicates (vector3 1 0) 0 1
          (make cylinder (center -0.5 0) 
             (radius r) (height infinity)
                     (material air)))
))

; add PML
(set! pml-layers (list (make pml (direction Y) (thickness dpml))))

; set up resolution
(set-param! resolution 30)

; set up test pulse
(define-param fcen 0.25) ; pulse center frequency
(define-param df 0.5); pulse freq. width: large df = short impulse

; place it off-center to excite all the possible modes
(define-param srcx 0.1234)
;(define-param srcy  0)

(set! sources (list
	       (make source
		 (src (make gaussian-src (frequency fcen) (fwidth df)))
		 (component Hz) (center srcx 0))))

; leverage Y-symmetry of the problem
(set! symmetries (list (make mirror-sym (direction Y) (phase -1))))

; set up k-point periodicity
; (need to do this before setting up flux regions)
(define-param k0 0.05)
(set-param! k-point (vector3 k0 0))

; capture EM flux through upper half plane
(define-param nfreq 200) ; number of frequencies at which to compute flux             


(define-param fluxx (- (/ sx 2) dpml ))
(define-param fluxy (* w 1.5 ))
(define-param fluxw (- sx (* 2 dpml )))
(define-param fluxh (* w 3 ))



(define upperflux ; flux at top of waveguide
      (add-flux fcen df nfreq
                    (make flux-region
                     (center 0 fluxy) (size fluxw 0) )))

(define rightflux ; flux to right of supercell
      (add-flux fcen df nfreq
                    (make flux-region
                     (center fluxx 0) (size 0 fluxh) )))

(define lowerflux ; flux out of bottom of waveguide
      (add-flux fcen df nfreq
                    (make flux-region
                     (center 0 (- fluxy)) (size fluxw 0) (weight -1.0) )))

(define leftflux ; flux to left of supercell
      (add-flux fcen df nfreq
                    (make flux-region
                     (center (- fluxx) 0) (size 0 fluxh) (weight -1.0) )))


; number of steps to run
(define-param T 300) 

(run-k-point T k-point)

(display-fluxes upperflux rightflux lowerflux leftflux)
