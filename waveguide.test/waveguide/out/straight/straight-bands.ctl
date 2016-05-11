; straight waveguide with a point source in the middle

(define-param eps 12)	; dielectric constant of waveguide
(define-param w 1.2)	; width of waveguide

(define-param sx 1) ; size of cell parallel to wvg.
(define-param sy 8) ; size of cell perp. to wvg.
(define-param dpml 1)	; pml thickness (y-dir only!)

; set up unit cell - repeating in x-direction
(set! geometry-lattice (make lattice (size sx sy no-size)))

; construct waveguide
(set! geometry
		(list (make block(center 0 0) (size infinity w infinity) 
			(material (make dielectric (epsilon eps))))))

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

; number of steps to run
(define-param T 300) 

; leverage Y-symmetry of the problem
(set! symmetries (list (make mirror-sym (direction Y) (phase -1))))

(define-param fluxx (- (/ sx 2) dpml ))
(define-param fluxy (* w 1.5 ))
(define-param fluxw (- sx (* 2 dpml )))
(define-param fluxh (* w 3 ))


; capture EM flux through upper half plane
(define-param nfreq 200) ; number of frequencies at which to compute flux       

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

(define-param flux-mode? false)

(define-param k-interp 50)

(if flux-mode? 
    (begin
		(run-sources+ T (dft-ldos fcen df nfreq))
		(display-fluxes upperflux rightflux lowerflux leftflux)
    )

    (begin
		(run-k-points T (interpolate k-interp (list (vector3 0) (vector3 0.5))))
    ))
