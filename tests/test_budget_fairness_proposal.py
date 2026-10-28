"""Illustrative fairness decision model only; not imported by the application."""
class ProposedWindow:
    def __init__(self,global_limit=10,client_limit=2,capacity=3):
        self.global_limit=global_limit;self.client_limit=client_limit;self.capacity=capacity
        self.total=0;self.clients={}
    def allow(self,identity):
        # Bounded overflow bucket: no eviction/reset of an active client's count.
        key=identity if identity in self.clients or len(self.clients)<self.capacity else 'overflow'
        used=self.clients.get(key,0)
        if used>=self.client_limit or self.total>=self.global_limit:return False
        self.clients[key]=used+1;self.total+=1;return True


def test_proposed_client_failures_do_not_spend_other_clients_global_capacity():
    budget=ProposedWindow()
    assert budget.allow('A') and budget.allow('A')
    assert all(not budget.allow('A') for _ in range(100))
    assert budget.total==2 and budget.allow('B')
    capped=ProposedWindow(global_limit=1)
    assert capped.allow('A') and not capped.allow('B')


def test_proposed_identity_storage_stays_bounded():
    budget=ProposedWindow(global_limit=1000)
    for i in range(1000):budget.allow(str(i))
    assert len(budget.clients)<=budget.capacity+1
