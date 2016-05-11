; straight waveguide with a point source in the middle

(define-param eps 12)	; dielectric constant of waveguide
(define-param w 1.2)	; width of waveguide
(define-param r 0.3)  ; radius of perturbation

(define-param sx 16) ; size of cell parallel to wvg.
(define-param sy 8) ; size of cell perp. to wvg.
(define-param dpml 1)	; pml thickness 

; set up unit cell - repeating in x-direction
(set! geometry-lattice (make lattice (size sx sy no-size)))

; construct waveguide
(set! geometry (append (list 

      (make block(center 0 0) (size infinity w infinity) 
        (material (make dielectric (epsilon eps)))))
      
      (geometric-objects-duplicates (vector3 1 0) -8 9
        (geometric-object-duplicates (vector3 0 (- w)) 0 1
          (make cylinder (center -0.5 (/ w 2)) 
             (radius r) (height infinity)
                     (material (make dielectric (epsilon eps))))))
                     ;(material air))))
))
; add PML
(set! pml-layers (list (make pml (thickness dpml))))

; set up resolution
(set-param! resolution 20)

; set up test pulse
(define-param fcen 0.25) ; pulse center frequency
(define-param df 1.0); pulse freq. width: large df = short impulse

; place it off-center to excite all the possible modes
(define-param srcx 0.1234)
;(define-param srcy  0)

(set! sources (list
	       (make source
		 (src (make gaussian-src (frequency fcen) (fwidth df)))
		 (component Hz) (center srcx 0))))

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
                     (center 0 (- fluxy)) (size fluxw 0) )))

(define leftflux ; flux to right of supercell
      (add-flux fcen df nfreq
                    (make flux-region
                     (center (- fluxx) 0) (size 0 fluxh) )))

; leverage Y-symmetry of the problem
(set! symmetries (list (make mirror-sym (direction Y) (phase -1))))

; number of steps to run
(define-param T 100) 

; interested in leaky modes in vertical direction
(set-param! k-point (vector3 0) )

(define-param output-field? false)

(run-sources+ T
  (at-beginning output-epsilon)
  (dft-ldos fcen df nfreq))
  ;(after-sources (harminv Hz (vector3 srcx) fcen df))
  ;(at-every (/ 1 fcen 20) output-hfield-z)

;(save-flux "flux-upper" upperflux)
;(save-flux "flux-right" rightflux)
;(save-flux "flux-lower" lowerflux)
;(save-flux "flux-left" leftflux)

(display-fluxes upperflux rightflux lowerflux leftflux)

(if output-field?
  (begin
    (reset-meep)
    (run-until (/ 3 fcen) (at-every (/ 1 fcen 20) output-hfield-z))
))

