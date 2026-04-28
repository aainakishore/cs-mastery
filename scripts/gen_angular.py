import json
from pathlib import Path

OUT = Path("/Users/eptr6dj/IdeaProjects/master-cs/cs-mastery/src/content/topics/angular")

def write(data):
    p = OUT / f"{data['id']}.json"
    p.write_text(json.dumps(data, indent=2))
    print(f"wrote {p.name}")

routing = {
    "id": "angular-routing", "unit": 10, "order": 102,
    "title": "Angular Routing",
    "summary": "Route configuration, lazy loading, route guards, resolvers, and navigation with Angular Router.",
    "prereqs": ["angular-services-di"],
    "guide": """# Angular Routing

Angular Router maps URL paths to components — first-match wins from top to bottom.

## Route Config
```typescript
export const routes: Routes = [
  { path: '',           component: HomeComponent },
  { path: 'products/:id', component: ProductDetailComponent },
  { path: 'admin', canActivate: [authGuard],
    loadChildren: () => import('./admin/admin.routes').then(m => m.adminRoutes) },
  { path: '**', component: NotFoundComponent }  // MUST be last
];
```

## Lazy Loading
```typescript
{ path: 'dashboard', loadComponent: () =>
    import('./dashboard.component').then(m => m.DashboardComponent) }
```

## Functional Guards (Angular 14+)
```typescript
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  return auth.isLoggedIn()
    ? true
    : inject(Router).createUrlTree(['/login'], { queryParams: { returnUrl: state.url } });
};
```

## Reading Route Params
```typescript
// One-time (snapshot):
const id = this.route.snapshot.paramMap.get('id');
// Reactive (same component, different params):
this.route.paramMap.pipe(map(p => p.get('id')))
```

## Resolvers
```typescript
export const productResolver: ResolveFn<Product> = (route) =>
  inject(ProductService).getProduct(route.paramMap.get('id')!);
// Route: { resolve: { product: productResolver } }
// Component: inject(ActivatedRoute).snapshot.data['product']
```

## Common Pitfalls
- `**` wildcard must be LAST.
- Guard returning `false` shows blank page — always return a UrlTree for redirect.
- Use `route.paramMap` Observable when same component navigates to different params.
- Child routes render in the PARENT component's `<router-outlet>`.
- NgModule apps: `RouterModule.forRoot(routes)`. Standalone: `provideRouter(routes)` in bootstrapApplication.
""",
    "questions": [
        {"id":"aro-q1","type":"mcq","prompt":"Why must `{ path: '**' }` be last?","choices":["TypeScript requirement","Angular matches top-to-bottom — wildcard first catches all URLs","Optional","Wildcards deprecated"],"answerIndex":1,"explanation":"First-match strategy: a wildcard route first would swallow all paths.","tags":["routing"]},
        {"id":"aro-q2","type":"mcq","prompt":"Main benefit of lazy-loaded routes?","choices":["Cache busting","Smaller initial bundle — route code downloads on first visit","Faster requests","Enables guards"],"answerIndex":1,"explanation":"Lazy loading splits the bundle. Rarely-visited pages (admin, reports) don't inflate the initial download.","tags":["routing","lazy-loading"]},
        {"id":"aro-q3","type":"mcq","prompt":"When to use `route.paramMap` Observable vs `snapshot`?","choices":["Always Observable","When same component navigates to different params without being destroyed","Only nested routes","Snapshot deprecated"],"answerIndex":1,"explanation":"Snapshot is frozen at init. If Angular reuses the component for new params, snapshot stays stale.","tags":["routing","route-params"]},
        {"id":"aro-q4","type":"mcq","prompt":"Guard returning `false` does what?","choices":["Redirects to home","Destroys component","Blocks navigation — page stays blank unless redirected","Logs warning"],"answerIndex":2,"explanation":"false blocks without redirecting. Use createUrlTree(['/login']) to properly redirect.","tags":["routing","guards"]},
        {"id":"aro-q5","type":"mcq","prompt":"`router.navigate(['/orders', '42', 'confirm'])` produces:","choices":["/orders/confirm","/orders/42/confirm","Error","Relative URL"],"answerIndex":1,"explanation":"Array segments become path parts: /orders/42/confirm.","tags":["routing"]},
        {"id":"aro-q6","type":"mcq","prompt":"Route Resolver purpose?","choices":["Guards access","Pre-fetches data before component activates — available synchronously in snapshot.data","Type-checks params","Handles 404"],"answerIndex":1,"explanation":"Resolver ensures data is ready before the view renders.","tags":["routing","resolver"]},
        {"id":"aro-q7","type":"mcq","prompt":"Standalone app equivalent of RouterModule.forRoot?","choices":["RouterModule.standalone","provideRouter(routes) in bootstrapApplication providers","Auto-discovered","RouterModule still needed"],"answerIndex":1,"explanation":"provideRouter(routes) is the functional standalone replacement.","tags":["routing","standalone"]},
        {"id":"aro-q8","type":"multi","prompt":"Valid Angular route guard types?","choices":["canActivate","canDeactivate","canDestroy","canMatch"],"answerIndexes":[0,1,3],"explanation":"canActivate, canDeactivate, canActivateChild, canMatch are real guards. canDestroy doesn't exist.","tags":["routing","guards"]},
        {"id":"aro-q9","type":"mcq","prompt":"Child routes render in which outlet?","choices":["Root AppComponent outlet","Parent route component's own <router-outlet>","Special child-outlet","First DOM outlet"],"answerIndex":1,"explanation":"Nested routes: parent must have its own <router-outlet> in its template.","tags":["routing","nested-routes"]},
        {"id":"aro-q10","type":"mcq","prompt":"canDeactivate guard typical use:","choices":["Admin auth","Unsaved-changes warning before navigating away","Lazy loading cleanup","HTTP cancellation"],"answerIndex":1,"explanation":"canDeactivate fires when leaving. Used for unsaved-form confirmation.","tags":["routing","canDeactivate"]}
    ],
    "flashcards": [
        {"id":"aro-fc1","front":"snapshot vs paramMap Observable","back":"snapshot: frozen at init. paramMap: reactive stream. Use Observable when same component navigates between different IDs.","tags":["routing"]},
        {"id":"aro-fc2","front":"loadComponent","back":"{ path: 'p', loadComponent: () => import('./p.component').then(m => m.PComponent) }. Separate JS chunk downloaded on first visit.","tags":["routing"]},
        {"id":"aro-fc3","front":"Guard return types","back":"true/false. UrlTree (createUrlTree(['/login'])): redirect. Observable<boolean|UrlTree>: async. Never return false alone.","tags":["routing","guards"]},
        {"id":"aro-fc4","front":"provideRouter (standalone)","back":"bootstrapApplication(App, { providers: [provideRouter(routes, withPreloading(...))] }). Functional and composable.","tags":["routing","standalone"]},
        {"id":"aro-fc5","front":"Resolver","back":"ResolveFn<T> = (route) => inject(Service).fetch(id). Route: resolve: { key: resolverFn }. Component reads: snapshot.data['key'].","tags":["routing"]},
        {"id":"aro-fc6","front":"Functional guard","back":"const g: CanActivateFn = (route, state) => { const a = inject(Auth); return a.loggedIn() ? true : inject(Router).createUrlTree(['/login']); }","tags":["routing","guards"]}
    ],
    "project": {
        "brief": "Design routing for a task app: public (/, /login), protected (dashboard, tasks, task-detail with resolver+canDeactivate), admin (role-guarded, lazy). Write the routes array and functional auth+role guards.",
        "checklist": [
            {"id":"c1","text":"Public routes eager; protected with canActivate: [authGuard]","weight":1},
            {"id":"c2","text":"Tasks and admin loaded via loadChildren (separate routes files)","weight":1},
            {"id":"c3","text":"Task detail: resolve: { task: taskResolver }, canDeactivate: [unsavedGuard]","weight":1},
            {"id":"c4","text":"authGuard returns createUrlTree(['/login'], { queryParams: { returnUrl: state.url } })","weight":1},
            {"id":"c5","text":"Admin guard reads user.role and returns createUrlTree(['/forbidden']) if not admin","weight":1}
        ],
        "hints": [
            "Functional guard: CanActivateFn = (route, state) => inject(Auth).isLoggedIn() ? true : inject(Router).createUrlTree(['/login', ...])",
            "returnUrl: after login use this.router.navigateByUrl(route.queryParams['returnUrl']) to restore destination.",
            "Routes file (not module): export const taskRoutes: Routes = [...]. loadChildren: () => import('./task.routes').then(m => m.taskRoutes)."
        ]
    }
}

forms = {
    "id": "angular-forms", "unit": 10, "order": 103,
    "title": "Angular Forms",
    "summary": "Template-driven vs reactive forms, FormControl, FormGroup, FormArray, validators, and form patterns.",
    "prereqs": ["angular-data-binding", "angular-rxjs"],
    "guide": """# Angular Forms

Two approaches: **template-driven** (model in template) and **reactive** (model in TypeScript).

## Reactive Forms with FormBuilder
```typescript
form = this.fb.group({
  email:    ['', [Validators.required, Validators.email]],
  password: ['', [Validators.required, Validators.minLength(8)]]
});

// Submit:
if (this.form.valid) { this.http.post('/auth', this.form.getRawValue()); }
```

## FormArray — Dynamic Fields
```typescript
get skills() { return this.form.get('skills') as FormArray; }
addSkill()            { this.skills.push(this.fb.control('')); }
removeSkill(i:number) { this.skills.removeAt(i); }
```

## Custom Validators
```typescript
// Sync
function noSpaces(ctrl:AbstractControl): ValidationErrors | null {
  return ctrl.value?.includes(' ') ? { noSpaces: true } : null;
}
// Cross-field (on FormGroup)
function passwordMatch(group:AbstractControl): ValidationErrors | null {
  return group.get('password')?.value === group.get('confirm')?.value
    ? null : { mismatch: true };
}
```

## State Flags
| Flag       | Meaning                          |
|-----------|----------------------------------|
| touched   | user focused + blurred           |
| dirty     | user changed the value           |
| valid     | all validators pass              |
| pending   | async validator running          |

Show error: `*ngIf="ctrl.invalid && ctrl.touched"`

## Common Pitfalls
- `form.value` excludes disabled controls; `form.getRawValue()` includes all.
- `patchValue` updates a subset; `setValue` requires all fields.
- Cast FormArray: `this.form.get('skills') as FormArray`.
- `ReactiveFormsModule` required for `[formGroup]` / `formControlName`.
- Async validators only fire after all sync validators pass.
""",
    "questions": [
        {"id":"arf-q1","type":"mcq","prompt":"Key difference: template-driven vs reactive forms?","choices":["Template-driven is newer","Source of truth: DOM for template-driven, TypeScript class for reactive. Reactive is synchronous, testable","Reactive requires backend","Template-driven has no validation"],"answerIndex":1,"explanation":"Reactive forms hold FormGroup in TypeScript — synchronous, predictable, unit-testable.","tags":["forms"]},
        {"id":"arf-q2","type":"mcq","prompt":"Why guard error display with `touched` or `dirty`?","choices":["Angola skips validation until touched","Showing 'required' before user interacts is bad UX — blank forms with red errors are confusing","Validators don't run","Only touched fields validate"],"answerIndex":1,"explanation":"Fields are invalid but untouched on load. Guard with touched/dirty to show errors only after interaction.","tags":["forms","UX"]},
        {"id":"arf-q3","type":"codeOutput","prompt":"form.value after patchValue?","code":"const f = new FormGroup({ name: new FormControl('Alice'), city: new FormControl('London') });\nf.patchValue({ name: 'Bob' });","choices":["{name:'Bob'}","{name:'Bob',city:'London'}","Error","city:null"],"answerIndex":1,"explanation":"patchValue only updates provided fields. city stays 'London'.","tags":["forms"]},
        {"id":"arf-q4","type":"mcq","prompt":"Custom validator return when valid?","choices":["true","{ valid:true }","null","{}"],"answerIndex":2,"explanation":"null = no error. { key: data } = error. control.errors is null when valid.","tags":["forms","validation"]},
        {"id":"arf-q5","type":"mcq","prompt":"Why use getRawValue() for submission?","choices":["Faster","form.value excludes disabled controls; getRawValue includes them","Same","Resolves async validators"],"answerIndex":1,"explanation":"Disabled fields excluded from form.value. Always use getRawValue() to get complete data.","tags":["forms"]},
        {"id":"arf-q6","type":"mcq","prompt":"Module for `[formGroup]` and `formControlName`?","choices":["FormsModule","CommonModule","ReactiveFormsModule","HttpClientModule"],"answerIndex":2,"explanation":"ReactiveFormsModule provides reactive directive bindings.","tags":["forms"]},
        {"id":"arf-q7","type":"mcq","prompt":"When do async validators fire?","choices":["Before sync","Simultaneously","Only after ALL sync validators pass","After 1 second"],"answerIndex":2,"explanation":"Angular short-circuits — no async HTTP calls if sync validation already fails.","tags":["forms","async-validators"]},
        {"id":"arf-q8","type":"multi","prompt":"Flags indicating user interaction?","choices":["dirty","touched","valid","pristine"],"answerIndexes":[0,1],"explanation":"dirty: changed value. touched: focused+blurred.","tags":["forms"]},
        {"id":"arf-q9","type":"mcq","prompt":"Cross-field validator placement?","choices":["Each control","FormGroup containing both fields","Submit handler","Async only"],"answerIndex":1,"explanation":"Cross-field validators receive the group — apply at FormGroup level.","tags":["forms"]},
        {"id":"arf-q10","type":"mcq","prompt":"Show ALL validation errors at once on submit?","choices":["form.validate()","form.markAllAsTouched()","form.showErrors()","form.submit()"],"answerIndex":1,"explanation":"markAllAsTouched() marks every control touched, triggering error display via touched guards.","tags":["forms"]}
    ],
    "flashcards": [
        {"id":"arf-fc1","front":"Validator return contract","back":"null = valid. { errorKey: data } = invalid. control.errors is null when valid. control.hasError('required') checks key.","tags":["forms"]},
        {"id":"arf-fc2","front":"patchValue vs setValue","back":"setValue: all fields required, throws if missing. patchValue: subset only, others unchanged.","tags":["forms"]},
        {"id":"arf-fc3","front":"getRawValue()","back":"Includes disabled controls; form.value excludes them. Use getRawValue() for form submission.","tags":["forms"]},
        {"id":"arf-fc4","front":"FormArray ops","back":"push(ctrl), removeAt(i), at(i), .controls array. Cast: form.get('items') as FormArray.","tags":["forms"]},
        {"id":"arf-fc5","front":"touched vs dirty","back":"touched: focused+blurred. dirty: changed. Show: ctrl.invalid && (ctrl.dirty || ctrl.touched). Call markAllAsTouched() on submit.","tags":["forms"]},
        {"id":"arf-fc6","front":"Cross-field validator","back":"new FormGroup({...}, { validators: matchFn }). matchFn receives group as AbstractControl. Return null (valid) or { key: true }.","tags":["forms"]}
    ],
    "project": {
        "brief": "Build a registration form: Account step (email with async availability check, password + confirm with cross-field match). Profile step (name, bio, dynamic skills FormArray). Design: async validator, cross-field validator, FormArray, error display, submit.",
        "checklist": [
            {"id":"c1","text":"Async email validator returns Observable<ValidationErrors|null>, fires only after sync pass","weight":1},
            {"id":"c2","text":"passwordMatch validator applied at FormGroup level","weight":1},
            {"id":"c3","text":"Skills FormArray with push() and removeAt(i), formArrayName in template","weight":1},
            {"id":"c4","text":"Errors guarded by touched; markAllAsTouched() on submit","weight":1},
            {"id":"c5","text":"Submit uses form.getRawValue()","weight":1}
        ],
        "hints": [
            "Async validator only fires after Validators.email passes — add it as sync validator to avoid wasted HTTP.",
            "skills: get skills() { return this.form.get('skills') as FormArray; }",
            "Template: formArrayName='skills', inner div with [formGroupName]='i'"
        ]
    }
}

signals = {
    "id": "angular-signals", "unit": 10, "order": 104,
    "title": "Angular Signals",
    "summary": "Signals, computed, effect, signal inputs/outputs, and fine-grained change detection.",
    "prereqs": ["angular-data-binding", "angular-rxjs"],
    "guide": """# Angular Signals

Signals (stable Angular 17) are reactive value containers. Angular tracks which template expressions read a signal and updates only those — surgical vs Zone.js broad-checking everything.

## Creating and Reading Signals
```typescript
const count = signal(0);       // WritableSignal<number>
count();                        // read: 0  — CALL the function!
count.set(5);                   // replace
count.update(v => v + 1);      // compute from old: 6
```

## computed — Lazy Derived Values
```typescript
const doubled = computed(() => count() * 2);  // memoized
// Recalculates ONLY when count() changes
```

## effect — Side Effects
```typescript
constructor() {
  effect(() => {
    document.body.className = this.theme();
    // Re-runs whenever theme() changes
  });
  // Must be called in injection context
}
```
**Use effect() for**: storage, analytics, non-Angular DOM.
**NOT for**: deriving values (use computed instead).

## Signal Inputs / Outputs (Angular 17.1+)
```typescript
label    = input<string>();             // InputSignal<string | undefined>
disabled = input(false);               // with default
size     = input.required<'sm'|'lg'>(); // required
clicked  = output<void>();             // OutputEmitterRef
value    = model(0);                   // two-way: [(value)]
```

## Bridging RxJS
```typescript
users    = toSignal(this.svc.users$(), { initialValue: [] });  // Observable → Signal
results$ = toObservable(searchTerm).pipe(debounceTime(300), switchMap(s => this.search(s)));
```

## Common Pitfalls
- Read with `()`: `count()` not `count`.
- Arrays: `arr.update(a => [...a, item])` not `arr().push(item)`.
- `effect()` must be in injection context.
- Never `effect(() => other.set(...))` — use `computed()`.
""",
    "questions": [
        {"id":"asig-q1","type":"mcq","prompt":"Primary advantage of signals over Zone.js?","choices":["Shorter syntax","Fine-grained: Angular knows exactly which expressions to re-evaluate when each signal changes","Signals replace all APIs","Zone.js is gone"],"answerIndex":1,"explanation":"Zone.js checks everything; signals carry targeted 'I changed' notifications.","tags":["signals","change-detection"]},
        {"id":"asig-q2","type":"codeOutput","prompt":"What does count() return?","code":"const count = signal(10);\ncount.update(v => v * 2);\ncount.set(5);\ncount.update(v => v + 3);\nconsole.log(count());","choices":["10","20","5","8"],"answerIndex":3,"explanation":"10 * 2 = 20; set(5) = 5; +3 = 8.","tags":["signals"]},
        {"id":"asig-q3","type":"mcq","prompt":"computed() recalculates:","choices":["Every CD cycle","Only when a signal it reads changes — lazy and memoized","Asynchronously","Never after init"],"answerIndex":1,"explanation":"computed() tracks reads. Recalculates on those signals changing only.","tags":["signals","computed"]},
        {"id":"asig-q4","type":"mcq","prompt":"Why use computed() not effect() for derived values?","choices":["Computed is faster","effect() → set() creates cycles; computed() is the correct reactive derivation tool","Identical","effect() can't read signals"],"answerIndex":1,"explanation":"effect(() => total.set(a() * b())) = cycle. Use computed(() => a() * b()).","tags":["signals","computed","effect"]},
        {"id":"asig-q5","type":"mcq","prompt":"What does model() provide?","choices":["Read-only input","Two-way bindable signal — parent binds with [(value)], component reads and updates","Model layer only","Async input"],"answerIndex":1,"explanation":"model() replaces @Input + @Output valueChange pair with a single two-way signal.","tags":["signals","model"]},
        {"id":"asig-q6","type":"mcq","prompt":"Where can effect() safely be called?","choices":["Anywhere","Only constructor","Injection context — constructor, field initializer, or runInInjectionContext","Only services"],"answerIndex":2,"explanation":"effect() registers cleanup on destroy via the injection context.","tags":["signals","effect"]},
        {"id":"asig-q7","type":"mcq","prompt":"What does toSignal(obs$) do?","choices":["Converts to Promise","Creates a Signal reflecting latest Observable value; auto-subscribes and auto-unsubscribes","Makes Observable sync","Wraps in BehaviorSubject"],"answerIndex":1,"explanation":"toSignal bridges RxJS → Signals. Synchronously readable in templates.","tags":["signals","rxjs-interop"]},
        {"id":"asig-q8","type":"multi","prompt":"Valid ways to mutate a WritableSignal?","choices":["count.set(5)","count.update(v => v+1)","count.mutate(arr => arr.push(x))","count.next(5)"],"answerIndexes":[0,1,2],"explanation":"set, update, mutate — the three mutation methods. .next() is RxJS.","tags":["signals"]},
        {"id":"asig-q9","type":"multi","prompt":"Valid use cases for effect()?","choices":["Sync signal to localStorage","Analytics on signal change","Derive a computed value","Sync document.title on title signal"],"answerIndexes":[0,1,3],"explanation":"effect() for side effects. computed() for derived values.","tags":["signals","effect"]},
        {"id":"asig-q10","type":"mcq","prompt":"Correct way to add an item to an array signal?","choices":["arr().push(item)","arr.update(a => [...a, item])","Arrays work like plain arrays","Signals don't support arrays"],"answerIndex":1,"explanation":"Signals track by reference. Push mutates in place — same reference, no update triggered.","tags":["signals","arrays"]}
    ],
    "flashcards": [
        {"id":"asig-fc1","front":"signal() mutations","back":"set(val): replace. update(fn): compute from old. mutate(fn): in-place (deprecated). Always read by calling: count() not count.","tags":["signals"]},
        {"id":"asig-fc2","front":"computed() guarantees","back":"Lazy, memoized, auto-tracked. Only recalculates when a read signal changes. Read-only — no set/update.","tags":["signals","computed"]},
        {"id":"asig-fc3","front":"effect() rules","back":"Side effects only. Injection context required. Never set another signal inside — use computed() for derivations.","tags":["signals","effect"]},
        {"id":"asig-fc4","front":"Signal inputs (Angular 17.1+)","back":"input<T>(): optional. input(default). input.required<T>(). Returns InputSignal — reactive, no ngOnChanges needed.","tags":["signals","signal-inputs"]},
        {"id":"asig-fc5","front":"toSignal / toObservable","back":"toSignal(obs$, { initialValue: [] }): Observable → Signal. toObservable(sig): Signal → Observable (for RxJS pipelines). Both require injection context.","tags":["signals","rxjs-interop"]},
        {"id":"asig-fc6","front":"Signals + OnPush","back":"Optimal combo — OnPush + signals. Angular tracks template signal reads. Updates only affected components. No markForCheck() needed.","tags":["signals","change-detection"]}
    ],
    "project": {
        "brief": "Design a live dashboard: (1) metrics Observable → toSignal; (2) selectedId: writable signal; (3) selectedMetric: computed from both; (4) theme toggle → effect to localStorage; (5) search: toObservable(term) → debounce → switchMap → toSignal. Where are signals vs computed vs effect?",
        "checklist": [
            {"id":"c1","text":"metrics = toSignal(svc.getMetrics$(), { initialValue: [] }) — Observable bridged to Signal","weight":1},
            {"id":"c2","text":"selectedId = signal<string|null>(null) — writable, user updates on click","weight":1},
            {"id":"c3","text":"selectedMetric = computed(() => metrics().find(m => m.id === selectedId()))","weight":1},
            {"id":"c4","text":"effect(() => localStorage.setItem('theme', theme())) — legitimate side effect","weight":1},
            {"id":"c5","text":"searchResults = toSignal(toObservable(term).pipe(debounceTime(300), switchMap(search)), { initialValue: [] })","weight":1}
        ],
        "hints": [
            "effect() must NOT set another signal — that's computed()'s domain.",
            "All toSignal/toObservable calls go in constructor (injection context).",
            "selectedMetric defaults to metrics()[0] if selectedId() is null."
        ]
    }
}

standalone = {
    "id": "angular-standalone", "unit": 10, "order": 105,
    "title": "Angular Standalone Components",
    "summary": "Standalone components and directives, bootstrapping without NgModule, functional providers, and migration.",
    "prereqs": ["angular-services-di", "angular-routing"],
    "guide": """# Angular Standalone Components

Standalone (stable Angular 15): each component declares its own imports — no NgModule required.

## Standalone Component
```typescript
@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    NgIf, NgFor, AsyncPipe,     // granular — tree-shakeable
    RouterLink, RouterOutlet,
    UserCardComponent,           // other standalone components
  ],
  template: `...`
})
export class DashboardComponent {}
```

## Bootstrapping
```typescript
bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes, withPreloading(PreloadAllModules)),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimations(),
  ]
});
// AppComponent must be standalone: true
```

## Functional Interceptor
```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthService).getToken();
  return next(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }));
};
```

## Lazy Loading
```typescript
{ path: 'settings', loadComponent: () =>
    import('./settings.component').then(m => m.SettingsComponent) }
{ path: 'admin',    loadChildren: () =>
    import('./admin/admin.routes').then(m => m.adminRoutes) }
```

## Tree-Shaking
Import `NgIf`, `NgFor` individually instead of `CommonModule` to tree-shake unused utilities.
Angular 17+ `@if`/`@for` need no import at all.

## Common Pitfalls
- `RouterOutlet` must be in imports for `<router-outlet>`.
- Non-standalone pipe/directive: wrap in a module, import that module.
- `provideHttpClient()` required in bootstrapApplication — not automatic.
- Tests: `imports: [MyStandaloneComponent]` not declarations.
""",
    "questions": [
        {"id":"ast-q1","type":"mcq","prompt":"What does `standalone: true` enable?","choices":["Run outside Angular","Component declares its own deps in imports[] — no NgModule needed","Lazy-loads by default","AOT-compiled only"],"answerIndex":1,"explanation":"Self-contained: imports[] replaces NgModule declarations for this component.","tags":["standalone"]},
        {"id":"ast-q2","type":"mcq","prompt":"Standalone replacement for RouterModule.forRoot?","choices":["RouterModule.standalone","provideRouter(routes) in bootstrapApplication providers","Auto-discovered","RouterModule still required"],"answerIndex":1,"explanation":"provideRouter(routes) is the composable functional provider for routing.","tags":["standalone","routing"]},
        {"id":"ast-q3","type":"mcq","prompt":"Why import NgIf/NgFor individually instead of CommonModule?","choices":["Faster execution","Tree-shaking — unused directives/pipes in CommonModule won't be bundled","Required for standalone","CommonModule deprecated"],"answerIndex":1,"explanation":"CommonModule bundles ~20 items. Individual imports let tree-shaker exclude unused ones.","tags":["standalone","tree-shaking"]},
        {"id":"ast-q4","type":"codeOutput","prompt":"Standalone component uses <router-outlet> but imports only CommonModule. What happens at runtime?","code":"@Component({ standalone: true, imports: [CommonModule], template: '<router-outlet></router-outlet>' })\nexport class AppComponent {}","choices":["Works fine","Compile error","Runtime: router-outlet is not a known element","Navigation disabled"],"answerIndex":2,"explanation":"RouterOutlet must be imported explicitly. Without it Angular reports unknown element.","tags":["standalone"]},
        {"id":"ast-q5","type":"mcq","prompt":"How to provide HttpClient in standalone app?","choices":["Import HttpClientModule in AppComponent","HttpClientModule in bootstrap providers","provideHttpClient() in bootstrapApplication providers","Automatic"],"answerIndex":2,"explanation":"provideHttpClient() (from @angular/common/http) is the functional replacement for HttpClientModule.","tags":["standalone","HttpClient"]},
        {"id":"ast-q6","type":"mcq","prompt":"Use standalone component in NgModule-based project?","choices":["Incompatible","Add to NgModule's imports array (not declarations)","Add to declarations","Bridge module required"],"answerIndex":1,"explanation":"Standalone components go in NgModule.imports — enables incremental migration.","tags":["standalone","migration"]},
        {"id":"ast-q7","type":"mcq","prompt":"TestBed for standalone component?","choices":["declarations: [Comp]","imports: [Comp] — brings own deps","TestBed.overrideComponent only","No TestBed needed"],"answerIndex":1,"explanation":"Standalone components are imported — they bring their own dependencies.","tags":["standalone","testing"]},
        {"id":"ast-q8","type":"multi","prompt":"Functional (non-class) providers in modern Angular?","choices":["provideRouter(routes)","provideHttpClient()","RouterModule.forRoot(routes)","provideAnimations()"],"answerIndexes":[0,1,3],"explanation":"provideRouter, provideHttpClient, provideAnimations are functional. RouterModule.forRoot is NgModule.","tags":["standalone","providers"]},
        {"id":"ast-q9","type":"mcq","prompt":"Functional HttpInterceptorFn vs class interceptor?","choices":["Identical","HttpInterceptorFn: plain function, inject() for services, registered via withInterceptors([fn])","Functions can't intercept","Class still required"],"answerIndex":1,"explanation":"No class, no implements keyword. Just register via withInterceptors.","tags":["standalone","HttpClient"]},
        {"id":"ast-q10","type":"mcq","prompt":"CLI command to migrate to standalone?","choices":["ng migrate standalone","ng generate @angular/core:standalone","ng convert standalone","ng standalone --migrate"],"answerIndex":1,"explanation":"ng generate @angular/core:standalone runs the official migration schematic.","tags":["standalone","migration","cli"]}
    ],
    "flashcards": [
        {"id":"ast-fc1","front":"standalone: true","back":"Component declares deps in imports[]. No NgModule needed. Direct import of other standalone components. Self-documenting, tree-shakeable.","tags":["standalone"]},
        {"id":"ast-fc2","front":"bootstrapApplication providers","back":"provideRouter(routes), provideHttpClient(), provideAnimations(). Functional, composable. Replaces AppModule + imports array.","tags":["standalone","bootstrap"]},
        {"id":"ast-fc3","front":"Functional interceptor","back":"const fn: HttpInterceptorFn = (req, next) => { const t = inject(Auth).getToken(); return next(req.clone({setHeaders:{Authorization:`Bearer ${t}`}})); }","tags":["standalone","HttpClient"]},
        {"id":"ast-fc4","front":"loadComponent vs loadChildren","back":"loadComponent: lazy single standalone component. loadChildren: lazy routes array file. Both split separate JS chunks.","tags":["standalone","lazy-loading"]},
        {"id":"ast-fc5","front":"Non-standalone in standalone","back":"Wrap in @NgModule({ declarations:[Comp], exports:[Comp] }). Import that module in standalone component's imports[].","tags":["standalone","migration"]},
        {"id":"ast-fc6","front":"Testing standalone","back":"TestBed.configureTestingModule({ imports: [MyComp], providers: [{ provide:Svc, useClass:Mock }] }). No declarations.","tags":["standalone","testing"]}
    ],
    "project": {
        "brief": "Migrate FeatureModule (ProductList, ProductDetail, SharedModule with TruncatePipe and HighlightDirective). Plan: (1) migration order; (2) SharedModule handling; (3) FeatureModule fate; (4) lazy loading; (5) ProductService scope after migration.",
        "checklist": [
            {"id":"c1","text":"Migrate leaf components first: standalone: true, move NgModule imports","weight":1},
            {"id":"c2","text":"TruncatePipe/HighlightDirective: make standalone OR keep in SharedModule imported by components","weight":1},
            {"id":"c3","text":"FeatureModule: delete or keep as thin re-export for backwards compat","weight":1},
            {"id":"c4","text":"Routing: loadChildren → import('./product.routes').then(m => m.productRoutes)","weight":1},
            {"id":"c5","text":"ProductService: providedIn: root → global singleton (behavior change from module-scoped)","weight":1}
        ],
        "hints": [
            "Start with leaf components — simplest imports.",
            "ProductService was module-scoped (new instance per lazy load). providedIn:root makes it a global singleton.",
            "Routes file (no module): export const productRoutes: Routes = [...]"
        ]
    }
}

write(routing)
write(forms)
write(signals)
write(standalone)
print("All done!")

